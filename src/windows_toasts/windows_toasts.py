from __future__ import annotations

from winsdk.windows.ui.notifications import ToastNotification, ToastNotificationManager

from .toast_document import ToastDocument
from .toast_types import Toast, ToastDuration


class WindowsToaster:
    def __init__(self, applicationId: str):
        self.toastNotifier = ToastNotificationManager.create_toast_notifier(applicationId)

    def show_toast(self, toast: Toast) -> None:
        """
        Displays the configured notification toast
        """
        toastContent = ToastDocument(ToastNotificationManager.get_template_content(toast.ToastType))
        if toast.hasImage and toast.imagePath is not None:
            toastContent.SetImageField(str(toast.imagePath))

        for i, fieldContent in enumerate(toast.textFields):
            toastContent.SetTextField(fieldContent, i)

        if toast.duration != ToastDuration.Default:
            toastContent.AddDuration(toast.duration.value)

        toastContent.SetAudioAttributes(toast.audio)

        notificationToSend = ToastNotification(toastContent.xmlDocument)
        if toast.on_activated is not None:
            notificationToSend.add_activated(lambda _, eventArgs: toast.on_activated(eventArgs))

        if toast.on_dismissed is not None:
            notificationToSend.add_dismissed(lambda _, eventArgs: toast.on_dismissed(eventArgs))

        if toast.on_activated is not None:
            notificationToSend.add_failed(lambda _, eventArgs: toast.on_failed(eventArgs))

        self.toastNotifier.show(notificationToSend)
