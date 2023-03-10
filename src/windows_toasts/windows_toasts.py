import warnings
from typing import Optional

from winsdk.windows.ui.notifications import ToastNotification, ToastNotificationManager, ToastNotifier

from .events import ToastActivatedEventArgs
from .toast_document import ToastDocument
from .toast_types import Toast, ToastDuration


class __BaseWindowsToaster:
    """
    Wrapper to simplify WinRT's ToastNotificationManager

    :param applicationText: Text to display the application as
    """
    applicationText: str
    toastNotifier: Optional[ToastNotifier]

    def __init__(self, applicationText: str):
        self.applicationText = applicationText
        self.toastNotifier = None

    def _setup_toast(self, toast: Toast) -> ToastDocument:
        """
        Setup toast to send. Should generally be used internally

        :return: XML built from a template of the supplied toast type
        """
        # noinspection DuplicatedCode
        toastContent = ToastDocument(ToastNotificationManager.get_template_content(toast.ToastType))
        if toast.HasImage and toast.imagePath is not None:
            toastContent.SetImageField(str(toast.imagePath))

        for i, fieldContent in enumerate(toast.textFields):
            toastContent.SetTextField(fieldContent, i)

        if toast.duration != ToastDuration.Default:
            toastContent.SetDuration(toast.duration.value)

        if toast.timestamp is not None:
            toastContent.SetCustomTimestamp(toast.timestamp)

        if toast.audio is not None:
            toastContent.SetAudioAttributes(toast.audio)

        return toastContent

    def show_toast(self, toast: Toast) -> None:
        """
        Display the passed notification toast
        :param toast: Toast to display
        """
        notificationToSend = ToastNotification(self._setup_toast(toast).xmlDocument)
        # noinspection DuplicatedCode
        if toast.on_activated is not None:
            # For some reason on_activated's type is generic, so cast it
            notificationToSend.add_activated(
                lambda _, eventArgs: toast.on_activated(ToastActivatedEventArgs.fromWinRt(eventArgs))
            )

        if toast.on_dismissed is not None:
            notificationToSend.add_dismissed(lambda _, eventArgs: toast.on_dismissed(eventArgs))

        if toast.on_failed is not None:
            notificationToSend.add_failed(lambda _, eventArgs: toast.on_failed(eventArgs))

        self.toastNotifier.show(notificationToSend)


class WindowsToaster(__BaseWindowsToaster):
    """
    Basic toaster, used to display toasts without actions and/or input fields.
    If you need to use them, see :class:`WindowsToaster`

    :param applicationText: Text to display the application as
    """

    def __init__(self, applicationText):
        super().__init__(applicationText)
        self.toastNotifier = ToastNotificationManager.create_toast_notifier(applicationText)

    def show_toast(self, toast):
        if len(toast.actions) > 0:
            warnings.warn(
                "Actions are not supported in WindowsToaster. If you'd like to use "
                "actions, instantiate a InteractableWindowsToaster class instead"
            )

        if toast.textInputPlaceholder is not None:
            warnings.warn(
                "Input fields are not supported in WindowsToaster. If you'd like to use "
                "input fields, instantiate a InteractableWindowsToaster class instead"
            )

        super().show_toast(toast)


class InteractableWindowsToaster(__BaseWindowsToaster):
    """
    :class:`WindowsToaster`, but uses an AUMI to support actions. Actions require a recognised AUMI to trigger
    on_activated,otherwise it triggers on_dismissed with no arguments

    :param applicationText: Text to display the application as
    :param notifierAUMI: AUMI to use. Defaults to Command Prompt. To use a custom AUMI, see one of the scripts
    """

    def __init__(self, applicationText: str, notifierAUMI: Optional[str] = None):
        super().__init__(applicationText)
        if notifierAUMI is None:
            self.defaultAUMI = True
            notifierAUMI = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\cmd.exe"
        else:
            self.defaultAUMI = False

        self.toastNotifier = ToastNotificationManager.create_toast_notifier(notifierAUMI)

    def _setup_toast(self, toast):
        toastContent = super()._setup_toast(toast)
        # If we haven't set up our own AUMI, put our application text in the attribution field
        if self.defaultAUMI:
            toastContent.SetAttributionText(self.applicationText)

        for customAction in toast.actions:
            toastContent.AddAction(customAction[0], customAction[1])

        if toast.textInputPlaceholder is not None:
            toastContent.SetInputField(toast.textInputPlaceholder)

        return toastContent

    def show_toast(self, toast: Toast):
        super().show_toast(toast)
