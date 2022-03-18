from winsdk.windows.ui.notifications import ToastNotification, ToastNotificationManager

from windows_toasts import ToastActivatedEventArgs, ToastDuration
from windows_toasts.toast_document import ToastDocument


# noinspection DuplicatedCode
class FakeWindowsToaster:
    def __init__(self, applicationText):
        self.applicationText = applicationText

    @staticmethod
    def setup_toast(toast):
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

        for customAction in toast.actions:
            toastContent.AddAction(customAction[0], customAction[1])

        if toast.textInputPlaceholder is not None:
            toastContent.SetInputField(toast.textInputPlaceholder)

        return toastContent

    def show_toast(self, toast):
        """
        Displays the passed notification toast
        """
        notificationToSend = ToastNotification(self.setup_toast(toast).xmlDocument)
        if toast.on_activated is not None:
            # For some reason on_activated's type is generic, so cast it
            notificationToSend.add_activated(
                lambda _, eventArgs: toast.on_activated(ToastActivatedEventArgs.fromWinRt(eventArgs))
            )

        if toast.on_dismissed is not None:
            notificationToSend.add_dismissed(lambda _, eventArgs: toast.on_dismissed(eventArgs))

        if toast.on_failed is not None:
            notificationToSend.add_failed(lambda _, eventArgs: toast.on_failed(eventArgs))


def test_simple_toast():
    try:
        from windows_toasts import ToastText1

        simpleToast = ToastText1()
        simpleToast.SetBody("Hello, simple world!")
        simpleToast.on_activated = lambda _: print("Toast clicked!")

        FakeWindowsToaster("Python").show_toast(simpleToast)
    except OSError as osError:
        if osError.winerror == -2143420155:
            print("The testing platform doesn't support notifications. Skipping test_simple_toast")
            return

        raise


def test_interactable_toast():
    try:
        from windows_toasts import ToastActivatedEventArgs, ToastImageAndText2

        def notificationActivated(activatedEventArgs: ToastActivatedEventArgs):
            print(f"Clicked event args: {activatedEventArgs.arguments}")
            print(activatedEventArgs.input)

        newToast = ToastImageAndText2()
        newToast.SetBody("Hello, interactable world!")
        newToast.AddAction("First", "clicked=first")
        newToast.AddAction("Second", "clicked=second")
        newToast.SetInputField("Write your placeholder text here!")

        newToast.on_activated = notificationActivated
        FakeWindowsToaster("Python").show_toast(newToast)
    except OSError as osError:
        if osError.winerror == -2143420155:
            print("The testing platform doesn't support notifications. Skipping test_interactable_toast")
            return

        raise


def test_audio_toast():
    try:
        from windows_toasts import AudioSource, ToastAudio, ToastText1

        newToast = ToastText1()
        newToast.audio = ToastAudio(AudioSource.IM, looping=True)

        FakeWindowsToaster("Python").show_toast(newToast)
    except OSError as osError:
        if osError.winerror == -2143420155:
            print("The testing platform doesn't support notifications. Skipping test_audio_toast")
            return

        raise
