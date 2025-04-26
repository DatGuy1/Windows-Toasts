import warnings
from datetime import datetime
from typing import Optional, TypeVar

from winrt.windows.ui.notifications import (
    NotificationData,
    NotificationUpdateResult,
    ScheduledToastNotification,
    ToastNotification,
    ToastNotificationHistory,
    ToastNotificationManager,
    ToastNotifier,
)

from .events import ToastActivatedEventArgs
from .exceptions import ToastNotFoundError
from .toast import Toast
from .toast_document import ToastDocument
from .wrappers import ToastDuration, ToastImagePosition, ToastScenario

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

    for i, fieldContent in enumerate(toast.text_fields):
        if fieldContent is not None:
            notificationData.values[f"text{i + 1}"] = fieldContent

    progressBar = toast.progress_bar
    if progressBar is not None:
        notificationData.values["status"] = progressBar.status
        notificationData.values.insert(
            "progress", "indeterminate" if progressBar.progress is None else str(progressBar.progress)
        )
        progressOverride = progressBar.progress_override
        if progressOverride is None and progressBar.progress is not None:
            # Recreate default Windows behaviour while still allowing it to be changed in the future
            progressOverride = f"{round(progressBar.progress * 100)}%"

        notificationData.values["progress_override"] = progressOverride
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
    # Group, a non-empty string, is required for some functionality. If one isn't provided, use the tag
    toastNotification.group = toast.group or toast.tag

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

        :return: XML built from the toast
        """
        # Should this be done in ToastDocument?
        toastContent = ToastDocument(toast)
        for image in toast.images:
            toastContent.AddImage(image)

        if toast.duration != ToastDuration.Default:
            toastContent.SetDuration(toast.duration)

        if toast.timestamp is not None:
            toastContent.SetCustomTimestamp(toast.timestamp)

        if toast.audio is not None:
            toastContent.SetAudioAttributes(toast.audio)

        if toast.attribution_text is not None:
            toastContent.SetAttributionText(toast.attribution_text)

        if toast.scenario != ToastScenario.Default:
            toastContent.SetScenario(toast.scenario)

        if toast.launch_action is not None:
            toastContent.SetAttribute(toastContent.GetElementByTagName("toast"), "launch", toast.launch_action)
            toastContent.SetAttribute(toastContent.GetElementByTagName("toast"), "activationType", "protocol")
        else:
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
        updateResult = self.toastNotifier.update_with_tag_and_group(newData, toast.tag, toast.group or toast.tag)
        return updateResult == NotificationUpdateResult.SUCCEEDED

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

    def unschedule_toast(self, toast: Toast) -> None:
        """
        Unschedule the passed notification toast

        :raises: ToastNotFoundError: If the toast could not be found
        """
        scheduledToasts = self.toastNotifier.get_scheduled_toast_notifications()
        targetNotification = next(
            (scheduledToast for scheduledToast in scheduledToasts if scheduledToast.tag == toast.tag), None
        )
        if targetNotification is None:
            raise ToastNotFoundError(f"Toast unscheduling failed. Toast {toast} not found")

        self.toastNotifier.remove_from_schedule(targetNotification)

    def clear_toasts(self) -> None:
        """
        Clear toasts popped by this toaster
        """
        toastHistory: ToastNotificationHistory = ToastNotificationManager.history
        toastHistory.clear_with_id(self._AUMID)

    def clear_scheduled_toasts(self) -> None:
        """
        Clear all scheduled toasts set for the toaster
        """
        scheduledToasts = self.toastNotifier.get_scheduled_toast_notifications()
        for toast in scheduledToasts:
            self.toastNotifier.remove_from_schedule(toast)

    def remove_toast(self, toast: Toast) -> None:
        """
        Removes an individual popped toast
        """
        # Is fetching toastHistory expensive? Should this be stored in an instance variable?
        toastHistory: ToastNotificationHistory = ToastNotificationManager.history
        toastHistory.remove_grouped_tag_with_id(toast.tag, toast.group or toast.tag, self._AUMID)

    def remove_toast_group(self, toastGroup: str) -> None:
        """
        Removes a group of toast notifications, identified by the specified group ID
        """
        toastHistory: ToastNotificationHistory = ToastNotificationManager.history
        toastHistory.remove_group_with_id(toastGroup, self._AUMID)


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
        self.notifierAUMID = None
        # .create_toast_notifier() fails with "Element not found"
        self.toastNotifier = ToastNotificationManager.create_toast_notifier_with_id(applicationText)

    def show_toast(self, toast: Toast) -> None:  # pragma: no cover
        if len(toast.inputs) > 0:
            warnings.warn(self.__InteractableWarningMessage.format("input fields"))

        if len(toast.actions) > 0:
            warnings.warn(self.__InteractableWarningMessage.format("actions"))

        if len(toast.images) > 2:
            warnings.warn(self.__InteractableWarningMessage.format("more than two images"))

        if toast.progress_bar is not None:
            warnings.warn(self.__InteractableWarningMessage.format("progress bars"))

        if any(toast_image.position == ToastImagePosition.Hero for toast_image in toast.images):
            warnings.warn(self.__InteractableWarningMessage.format("hero placements"))

        super().show_toast(toast)

    def _setup_toast(self, toast, dynamic) -> ToastDocument:
        toastContent = super()._setup_toast(toast, dynamic)

        for i, fieldContent in enumerate(toast.text_fields):
            if fieldContent is None:
                fieldContent = ""

            if dynamic:
                toastContent.SetTextField(i)
            else:
                toastContent.SetTextFieldStatic(i, fieldContent)

        toastContent.SetAttribute(toastContent.bindingNode, "template", "ToastImageAndText04")

        return toastContent


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

        self.toastNotifier = ToastNotificationManager.create_toast_notifier_with_id(self.notifierAUMID)

    def _setup_toast(self, toast, dynamic):
        toastContent = super()._setup_toast(toast, dynamic)

        for i, fieldContent in enumerate(toast.text_fields):
            if fieldContent is None:
                continue

            if dynamic:
                toastContent.SetTextField(i)
            else:
                toastContent.SetTextFieldStatic(i, fieldContent)

        toastContent.SetAttribute(toastContent.bindingNode, "template", "ToastGeneric")
        toastNode = toastContent.GetElementByTagName("toast")
        toastContent.SetAttribute(toastNode, "useButtonStyle", "true")

        # If we haven't set up our own AUMID, put our application text in the attribution field
        if self.defaultAUMID and toast.attribution_text is None:
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
