from pytest import warns
from winsdk.windows.ui.notifications import ToastNotification, ToastNotificationManager

from windows_toasts import ToastActivatedEventArgs, ToastDuration
from windows_toasts.toast_document import ToastDocument


# noinspection DuplicatedCode
class FakeWindowsToaster:
    def __init__(self, applicationText):
        self.applicationText = applicationText
        self.toastNotifier = ToastNotificationManager.create_toast_notifier(applicationText)

    @staticmethod
    def setup_toast(toast):
        toastContent = ToastDocument(ToastNotificationManager.get_template_content(toast.ToastType))
        if toast.HasImage and toast.imagePath is not None:
            toastContent.SetImageField(toast.imagePath)

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

        self.toastNotifier.show(notificationToSend)


def test_simple_toast():
    from windows_toasts import ToastText3

    simpleToast = ToastText3()

    simpleToast.SetHeadline("Hello, World!")
    simpleToast.SetFirstLine("Foobar")

    simpleToast.on_activated = lambda _: print("Toast clicked!")

    FakeWindowsToaster("Python").show_toast(simpleToast)


def test_interactable_toast():
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


def test_audio_toast():
    from windows_toasts import AudioSource, ToastAudio, ToastText2

    toaster = FakeWindowsToaster("Python")

    newToast = ToastText2()
    newToast.audio = ToastAudio(AudioSource.IM, looping=True)

    toaster.show_toast(newToast)

    newToast.audio.silent = True

    toaster.show_toast(newToast)


def test_warnings_toast():
    from windows_toasts import ToastText1

    newToast = ToastText1()
    with warns(UserWarning, match="has no headline, only a body"):
        newToast.SetHeadline("Hello, World!")

    with warns(UserWarning, match="does not support images"):
        newToast.SetImage("C:/Windows/System32/@WLOGO_96x96.png")

    assert len(newToast.textFields) == 1
    assert newToast.textFields[0] == "Hello, World!"

    for i in range(1, 6):
        newToast.AddAction(f"Button #{i}", str(i))

    with warns(UserWarning, match="Cannot add any more actions, you've already reached five"):
        newToast.AddAction("Button 6", str(6))

    assert len(newToast.actions) == 5
    for i, toastAction in enumerate(newToast.actions):
        assert newToast.actions[i] == (f"Button #{i + 1}", str(i + 1))

    FakeWindowsToaster("Python").show_toast(newToast)


def test_image_toast():
    from windows_toasts import ToastImageAndText4

    newToast = ToastImageAndText4()

    newToast.SetHeadline("Hello, World!")
    newToast.SetFirstLine("Foo")
    newToast.SetSecondLine("Bar")

    newToast.SetImage("https://www.python.org/static/community_logos/python-powered-h-140x182.png")
    newToast.SetImage("C:/Windows/System32/@WLOGO_96x96.png")

    FakeWindowsToaster("Python").show_toast(newToast)


def test_custom_timestamp_toast():
    from datetime import datetime, timedelta

    from windows_toasts import ToastText4

    newToast = ToastText4()
    newToast.SetCustomTimestamp(datetime.utcnow() - timedelta(hours=1))

    FakeWindowsToaster("Python").show_toast(newToast)


def test_input_toast():
    from windows_toasts import ToastImageAndText1

    newToast = ToastImageAndText1()
    newToast.SetBody("You. Yes, you.")
    newToast.SetInputField("What's on your mind?")

    FakeWindowsToaster("Python").show_toast(newToast)


def test_attribution_text_toast():
    from windows_toasts import ToastImageAndText3

    newToast = ToastImageAndText3()
    newToast.SetHeadline("Hello, World!")
    newToast.SetFirstLine("Foobar")

    FakeToaster = FakeWindowsToaster("Python")
    toastContent = FakeToaster.setup_toast(newToast)
    toastContent.SetAttributionText("Windows-Toasts")

    FakeToaster.toastNotifier.show(ToastNotification(toastContent.xmlDocument))
