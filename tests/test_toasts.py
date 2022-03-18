def test_simple_toast():
    try:
        from windows_toasts import ToastText1, WindowsToaster

        simpleToast = ToastText1()
        simpleToast.SetBody("Hello, simple world!")
        simpleToast.on_activated = lambda _: print("Toast clicked!")

        WindowsToaster("Python").show_toast(simpleToast)
    except OSError as osError:
        if osError.winerror == -2143420155:
            print("The testing platform doesn't support notifications. Skipping test_simple_toast")
            return

        raise


def test_interactable_toast():
    try:
        from windows_toasts import (
            AudioSource, InteractableWindowsToaster, ToastActivatedEventArgs, ToastAudio, ToastImageAndText2
        )

        def notificationActivated(activatedEventArgs: ToastActivatedEventArgs):
            print(f"Clicked event args: {activatedEventArgs.arguments}")
            print(activatedEventArgs.input)

        newToast = ToastImageAndText2()
        newToast.SetBody("Hello, interactable world!")
        newToast.AddAction("First", "clicked=first")
        newToast.AddAction("Second", "clicked=second")
        newToast.SetInputField("Write your placeholder text here!")

        newToast.on_activated = notificationActivated
        InteractableWindowsToaster("Python").show_toast(newToast)
    except OSError as osError:
        if osError.winerror == -2143420155:
            print("The testing platform doesn't support notifications. Skipping test_interactable_toast")
            return

        raise


def test_audio_toast():
    try:
        from windows_toasts import (
            AudioSource, WindowsToaster, ToastAudio, ToastText1
        )
        newToast = ToastText1()
        newToast.audio = ToastAudio(AudioSource.IM, looping=True)

        WindowsToaster("Python").show_toast(newToast)
    except OSError as osError:
        if osError.winerror == -2143420155:
            print("The testing platform doesn't support notifications. Skipping test_audio_toast")
            return

        raise
