import warnings
from datetime import datetime
from typing import TypeVar, cast

from winrt.windows.data.xml.dom import IXmlNode
from winrt.windows.ui.notifications import (
    NotificationData,
    NotificationUpdateResult,
    ScheduledToastNotification,
    ToastNotification,
    ToastNotificationHistory,
    ToastNotificationManager,
    ToastNotifier,
)

from .events import ToastActivatedEventArgs, ToastDismissedEventArgs, ToastFailedEventArgs
from .exceptions import ToastNotFoundError
from .toast import ActionCenterToast, Toast
from .toast_document import ToastDocument
from .wrappers import (
    NotificationSetting,
    ToastDuration,
    ToastImagePosition,
    ToastNotificationMode,
    ToastProgressBar,
    ToastScenario,
)

#: A ToastNotification or ScheduledToastNotification, for code that builds either
ToastNotificationT = TypeVar("ToastNotificationT", ToastNotification, ScheduledToastNotification)

# HRESULT_FROM_WIN32(ERROR_NOT_FOUND), raised for an AUMID Windows has no notification settings for yet
_E_ELEMENT_NOT_FOUND = 0x80070490


def _default_progress_override(progress: float) -> str:
    """
    The text Windows shows next to a progress bar by default
    """
    return f"{round(progress * 100)}%"


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
        notificationData.values["progress"] = (
            "indeterminate" if progressBar.progress is None else str(progressBar.progress)
        )
        progressOverride = progressBar.progress_override
        if progressOverride is None and progressBar.progress is not None:
            # Recreate default Windows behaviour while still allowing it to be changed in the future
            progressOverride = _default_progress_override(progressBar.progress)

        # The map only takes strings, so an indeterminate bar without an override gets an empty one
        notificationData.values["progress_override"] = progressOverride or ""
        notificationData.values["caption"] = progressBar.caption or ""

    return notificationData


def _read_action_center_toast(notification: ToastNotification) -> ActionCenterToast | None:
    """
    Read a toast from Action Center, filling in the values :func:`_build_adaptable_data` bound to it

    :return: None if Windows can't read the toast's tag or group
    """
    try:
        tag, group = notification.tag, notification.group
    except OSError:
        return None

    # pywinrt's stubs don't say so, but these are None for a toast shown without data or an attribute that's missing
    data = cast(NotificationData | None, notification.data)
    values = {} if data is None else dict(data.values.items())

    def resolve(value: str | None) -> str | None:
        # A data binding placeholder, such as {text1}, rather than text shown as-is
        if value is not None and value.startswith("{") and value.endswith("}"):
            value = values.get(value[1:-1])

        return value or None

    content = notification.content
    textFields = tuple(
        resolve(node.inner_text) for node in content.select_nodes("/toast/visual/binding/text[not(@placement)]")
    )

    progressBar = None
    progressNode = content.select_single_node("/toast/visual/binding/progress")
    if progressNode is not None:

        def attribute(name: str) -> str | None:
            node = cast(IXmlNode | None, progressNode.attributes.get_named_item(name))
            return resolve(None if node is None else node.inner_text)

        try:
            progress = float(attribute("value") or "")
        except ValueError:
            # "indeterminate"
            progress = None

        progressOverride = attribute("valueStringOverride")
        # _build_adaptable_data fills in the default when there's no override, which would otherwise stick
        if progress is not None and progressOverride == _default_progress_override(progress):
            progressOverride = None

        progressBar = ToastProgressBar(attribute("status") or "", attribute("title"), progress, progressOverride)

    return ActionCenterToast(
        tag=tag,
        # _build_toast_notification uses the tag when the toast has no group
        group=None if group in ("", tag) else group,
        text_fields=textFields,
        progress_bar=progressBar,
        expiration_time=notification.expiration_time,
    )


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

    # ScheduledToastNotification doesn't have this property
    if isinstance(toastNotification, ToastNotification):
        toastNotification.expires_on_reboot = toast.expires_on_reboot

    return toastNotification


class BaseWindowsToaster:
    """
    Wrapper to simplify WinRT's ToastNotificationManager

    :param applicationText: Text to display the application as
    """

    applicationText: str
    notifierAUMID: str | None
    toastNotifier: ToastNotifier

    def __init__(self, applicationText: str) -> None:
        self.applicationText = applicationText

    @property
    def _AUMID(self) -> str:
        return self.notifierAUMID or self.applicationText

    @property
    def notification_setting(self) -> NotificationSetting | None:
        """
        Whether Windows will show this toaster's notifications, and if not, why.

        :return: None if Windows doesn't know the toaster's AUMID yet, which is the case until it shows its first toast
        """
        try:
            return NotificationSetting(self.toastNotifier.setting)
        except OSError as e:
            if e.winerror is not None and e.winerror & 0xFFFFFFFF == _E_ELEMENT_NOT_FOUND:
                return None
            raise

    @property
    def notification_mode(self) -> ToastNotificationMode:
        """
        Which notifications Windows currently lets through for the user, such as while Do Not Disturb is on.
        This applies to the whole user, not just this toaster
        """
        return ToastNotificationMode(ToastNotificationManager.get_default().notification_mode)

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

        if toast.header is not None:
            toastContent.SetHeader(toast.header)

        toastNode = toastContent.GetElementByTagName("toast")
        launchAction = toast.launch_action
        if launchAction is not None:
            toastContent.SetAttribute(toastNode, "launch", launchAction)
            toastContent.SetAttribute(toastNode, "activationType", "protocol")
        else:
            toastContent.SetAttribute(toastNode, "launch", toast.tag)

        return toastContent

    def show_toast(self, toast: Toast) -> None:
        """
        Displays the specified toast notification.
        If `toast` has already been shown, it will pop up again, but make no new sections in Action Center

        :param toast: Toast to display
        """
        toastNotification = ToastNotification(self._setup_toast(toast, True).xmlDocument)
        toastNotification.data = _build_adaptable_data(toast)

        # Copied to locals so the type checker knows they aren't None inside the lambdas
        onActivated, onDismissed, onFailed = toast.on_activated, toast.on_dismissed, toast.on_failed

        if onActivated is not None:  # pragma: no cover
            toastNotification.add_activated(
                lambda _, eventArgs: onActivated(ToastActivatedEventArgs.fromWinRt(eventArgs))
            )

        if onDismissed is not None:  # pragma: no cover
            toastNotification.add_dismissed(
                lambda _, eventArgs: onDismissed(ToastDismissedEventArgs.fromWinRt(eventArgs))
            )

        if onFailed is not None:  # pragma: no cover
            toastNotification.add_failed(lambda _, eventArgs: onFailed(ToastFailedEventArgs.fromWinRt(eventArgs)))

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
        updateResult = self.toastNotifier.update(newData, toast.tag, toast.group or toast.tag)
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
            (
                scheduledToast
                for scheduledToast in scheduledToasts
                if (scheduledToast.tag, scheduledToast.group) == (toast.tag, toast.group or toast.tag)
            ),
            None,
        )
        if targetNotification is None:
            raise ToastNotFoundError(f"Toast unscheduling failed. Toast {toast} not found")

        self.toastNotifier.remove_from_schedule(targetNotification)

    def clear_toasts(self) -> None:
        """
        Clear toasts popped by this toaster
        """
        toastHistory: ToastNotificationHistory = ToastNotificationManager.history
        toastHistory.clear(self._AUMID)

    def get_action_center_toasts(self) -> list[ActionCenterToast]:
        """
        Get the toasts in Action Center that were shown under this toaster's AUMID. Their content is what they were
        shown with, so changes from :meth:`update_toast` aren't reflected.
        :class:`InteractableWindowsToaster`'s default AUMID is shared, so it includes other programs' toasts too

        :return: The toasts, which you can find yours in by :attr:`~windows_toasts.toast.Toast.tag`
        """
        toastHistory: ToastNotificationHistory = ToastNotificationManager.history
        toasts = (_read_action_center_toast(notification) for notification in toastHistory.get_history(self._AUMID))
        return [toast for toast in toasts if toast is not None]

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
        toastHistory.remove(toast.tag, toast.group or toast.tag, self._AUMID)

    def remove_toast_group(self, toastGroup: str) -> None:
        """
        Removes a group of toast notifications, identified by the specified group ID
        """
        toastHistory: ToastNotificationHistory = ToastNotificationManager.history
        toastHistory.remove_group(toastGroup, self._AUMID)


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

    def __init__(self, applicationText: str) -> None:
        super().__init__(applicationText)
        self.notifierAUMID = None
        # .create_toast_notifier() without an AUMID fails with "Element not found"
        self.toastNotifier = ToastNotificationManager.create_toast_notifier(applicationText)

    def show_toast(self, toast: Toast) -> None:  # pragma: no cover
        if len(toast.inputs) > 0:
            warnings.warn(self.__InteractableWarningMessage.format("input fields"), stacklevel=2)

        if len(toast.actions) > 0:
            warnings.warn(self.__InteractableWarningMessage.format("actions"), stacklevel=2)

        if len(toast.images) > 1:
            warnings.warn(self.__InteractableWarningMessage.format("multiple images"), stacklevel=2)

        if toast.progress_bar is not None:
            warnings.warn(self.__InteractableWarningMessage.format("progress bars"), stacklevel=2)

        if len(toast.groups) > 0:
            warnings.warn(self.__InteractableWarningMessage.format("groups"), stacklevel=2)

        if any(toast_image.position == ToastImagePosition.Hero for toast_image in toast.images):
            warnings.warn(self.__InteractableWarningMessage.format("hero placements"), stacklevel=2)

        super().show_toast(toast)

    def _setup_toast(self, toast: Toast, dynamic: bool) -> ToastDocument:
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

    def __init__(self, applicationText: str, notifierAUMID: str | None = None) -> None:
        super().__init__(applicationText)
        self.defaultAUMID = notifierAUMID is None
        if notifierAUMID is None:
            notifierAUMID = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\cmd.exe"

        self.notifierAUMID = notifierAUMID
        self.toastNotifier = ToastNotificationManager.create_toast_notifier(notifierAUMID)

    def _setup_toast(self, toast: Toast, dynamic: bool) -> ToastDocument:
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

        for group in toast.groups:
            toastContent.AddGroup(group)

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
