import warnings
from datetime import datetime
from typing import Optional, TypeVar

from winsdk.windows.ui.notifications import (
    NotificationData,
    NotificationUpdateResult,
    ScheduledToastNotification,
    ToastNotification,
    ToastNotificationHistory,
    ToastNotificationManager,
    ToastNotifier,
)

from .events import ToastActivatedEventArgs
from .toast_document import ToastDocument
from .toast_types import Toast
from .wrappers import ToastDuration, ToastScenario

ToastNotificationT = TypeVar("ToastNotificationT", ToastNotification, ScheduledToastNotification)


def _build_adaptable_data(toast: Toast) -> NotificationData:
    """
    Build the adaptable content from a toast

    :param toast: Toast that has adaptable content
    :type toast: Toast
    :return: A NotificationData object ready to be used in ToastNotifier.Update
    :rtype: NotificationData
    """
    notificationData = NotificationData()

    toast.updates += 1
    notificationData.sequence_number = toast.updates

    for i, fieldContent in enumerate(toast.textFields):
        notificationData.values[f"text{i + 1}"] = fieldContent

    progressBar = toast.progress_bar
    if progressBar is not None:
        notificationData.values["status"] = progressBar.status
        notificationData.values.insert(
            "progress", "indeterminate" if progressBar.progress is None else str(progressBar.progress)
        )
        notificationData.values["progress_override"] = progressBar.progress_override or ""
        notificationData.values["caption"] = progressBar.caption or ""

    return notificationData


def _build_toast_notification(toast: Toast, toastNotification: ToastNotificationT) -> ToastNotificationT:
    """
    Builds a ToastNotification appropriately
    :param toast: The toast with the bindings
    :type toastNotification: ToastNotificationGeneric
    :rtype: ToastNotificationT
    """
    toastNotification.tag = toast.tag
    if toast.group is not None:
        toastNotification.group = toast.group

    if toast.expiration_time is not None:
        toastNotification.expiration_time = toast.expiration_time

    toastNotification.suppress_popup = toast.suppress_popup

    return toastNotification


class BaseWindowsToaster:
    """
    Wrapper to simplify WinRT's ToastNotificationManager

    :param applicationText: Text to display the application as
    """

    applicationText: str
    notifierAUMID: Optional[str]
    toastNotifier: ToastNotifier

    def __init__(self, applicationText: str):
        self.applicationText = applicationText

    @property
    def _AUMID(self) -> str:
        return self.notifierAUMID or self.applicationText

    def _setup_toast(self, toast: Toast, dynamic: bool) -> ToastDocument:
        """
        Setup toast to send. Should generally be used internally

        :return: XML built from a template of the supplied toast type
        """
        # Should this be done in ToastDocument?
        toastContent = ToastDocument(ToastNotificationManager.get_template_content(toast.ToastType))
        if toast.HasImage:
            for image in toast.images:
                toastContent.AddImage(image)

        for i, fieldContent in enumerate(toast.textFields):
            if dynamic:
                toastContent.SetTextField(i)
            else:
                toastContent.SetTextFieldStatic(i, fieldContent)

        if toast.duration != ToastDuration.Default:
            toastContent.SetDuration(toast.duration)

        if toast.timestamp is not None:
            toastContent.SetCustomTimestamp(toast.timestamp)

        if toast.audio is not None:
            toastContent.SetAudioAttributes(toast.audio)

        if toast.scenario != ToastScenario.Default:
            toastContent.SetScenario(toast.scenario)

        toastContent.SetAttribute(toastContent.GetElementByTagName("toast"), "launch", toast.tag)
        return toastContent

    def show_toast(self, toast: Toast) -> None:
        """
        Displays the specified toast notification.
        If `toast` has already been shown, it will pop up again, but make no new sections in the action center

        :param toast: Toast to display
        """
        toastNotification = ToastNotification(self._setup_toast(toast, True).xmlDocument)
        toastNotification.data = _build_adaptable_data(toast)

        if toast.on_activated is not None:  # pragma: no cover
            # For some reason on_activated's type is generic, so cast it
            toastNotification.add_activated(
                lambda _, eventArgs: toast.on_activated(ToastActivatedEventArgs.fromWinRt(eventArgs))
            )

        if toast.on_dismissed is not None:  # pragma: no cover
            toastNotification.add_dismissed(lambda _, eventArgs: toast.on_dismissed(eventArgs))

        if toast.on_failed is not None:  # pragma: no cover
            toastNotification.add_failed(lambda _, eventArgs: toast.on_failed(eventArgs))

        notificationToSend = _build_toast_notification(toast, toastNotification)

        self.toastNotifier.show(notificationToSend)

    def update_toast(self, toast: Toast) -> bool:
        """
        Update the passed notification data with the new data in the clas

        :param toast: Toast to update
        :type toast: Toast
        :return: Whether the update succeeded
        """
        newData = _build_adaptable_data(toast)
        return self.toastNotifier.update(newData, toast.tag) == NotificationUpdateResult.SUCCEEDED

    def schedule_toast(self, toast: Toast, displayTime: datetime) -> None:
        """
        Schedule the passed notification toast. Warning: scheduled toasts cannot be updated or activated (i.e. on_X)

        :param toast: Toast to display
        :type toast: Toast
        :param displayTime: Time to display the toast on
        :type displayTime: datetime
        """
        toastNotification = ScheduledToastNotification(self._setup_toast(toast, False).xmlDocument, displayTime)
        scheduledNotificationToSend = _build_toast_notification(toast, toastNotification)

        self.toastNotifier.add_to_schedule(scheduledNotificationToSend)

    def unschedule_toast(self, toast: Toast) -> bool:
        """
        Unschedule the passed notification toast

        :return: Whether the unscheduling failed or succeeded
        """
        scheduledToasts = self.toastNotifier.get_scheduled_toast_notifications()
        targetNotification = next(
            (scheduledToast for scheduledToast in scheduledToasts if scheduledToast.tag == toast.tag), None
        )
        if targetNotification is None:
            warnings.warn(f"Toast unscheduling failed. Toast {toast} not found")
            return False

        self.toastNotifier.remove_from_schedule(targetNotification)
        return True

    def clear_toasts(self) -> None:
        """
        Clear toasts popped by this toaster
        """
        # noinspection PyUnresolvedReferences
        toastHistory: ToastNotificationHistory = ToastNotificationManager.get_history()
        toastHistory.clear(self._AUMID)

    def clear_scheduled_toasts(self) -> None:
        """
        Clear all scheduled toasts set for the toaster
        """
        scheduledToasts = self.toastNotifier.get_scheduled_toast_notifications()
        for toast in scheduledToasts:
            self.toastNotifier.remove_from_schedule(toast)


class WindowsToaster(BaseWindowsToaster):
    """
    Basic toaster, used to display toasts without actions and/or inputs.
    If you need to use them, see :class:`InteractableWindowsToaster`

    :param applicationText: Text to display the application as
    """

    __InteractableWarningMessage = (
        "{0} are not supported in WindowsToaster. If you'd like to use {0}, "
        "instantiate a InteractableWindowsToaster class instead"
    )

    def __init__(self, applicationText: str):
        super().__init__(applicationText)
        self.notifierAUMI = None
        self.toastNotifier = ToastNotificationManager.create_toast_notifier(applicationText)

    def show_toast(self, toast: Toast) -> None:  # pragma: no cover
        if len(toast.inputs) > 0:
            warnings.warn(self.__InteractableWarningMessage.format("input fields"))

        if len(toast.actions) > 0:
            warnings.warn(self.__InteractableWarningMessage.format("actions"))

        if toast.progress_bar is not None:
            warnings.warn(self.__InteractableWarningMessage.format("progress bars"))

        if any(toast_image.large for toast_image in toast.images):
            warnings.warn(self.__InteractableWarningMessage.format("large images"))

        super().show_toast(toast)


class InteractableWindowsToaster(BaseWindowsToaster):
    """
    :class:`WindowsToaster`, but uses a AUMID to support actions. Actions require a recognised AUMID to trigger
    on_activated, otherwise it triggers on_dismissed with no arguments

    :param applicationText: Text to display the application as
    :param notifierAUMID: AUMID to use. Defaults to Command Prompt. To use a custom AUMID, see one of the scripts
    """

    def __init__(self, applicationText: str, notifierAUMID: Optional[str] = None):
        super().__init__(applicationText)
        if notifierAUMID is None:
            self.defaultAUMID = True
            self.notifierAUMID = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\cmd.exe"
        else:
            self.defaultAUMID = False
            self.notifierAUMID = notifierAUMID

        self.toastNotifier = ToastNotificationManager.create_toast_notifier(self.notifierAUMID)

    def _setup_toast(self, toast, dynamic):
        toastContent = super()._setup_toast(toast, dynamic)

        bindingNode = toastContent.GetElementByTagName("binding")
        toastContent.SetAttribute(bindingNode, "template", "ToastGeneric")
        toastNode = toastContent.GetElementByTagName("toast")
        toastContent.SetAttribute(toastNode, "useButtonStyle", "true")

        # If we haven't set up our own AUMID, put our application text in the attribution field
        if self.defaultAUMID:
            toastContent.SetAttributionText(self.applicationText)

        for toastInput in toast.inputs:
            toastContent.AddInput(toastInput)

        for customAction in toast.actions:
            toastContent.AddAction(customAction)

        if toast.progress_bar is not None:
            if dynamic:
                toastContent.AddProgressBar()
            else:
                toastContent.AddStaticProgressBar(toast.progress_bar)

        return toastContent
