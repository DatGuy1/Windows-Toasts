import copy

from pytest import raises, warns
from toasts_winrt.windows.ui.notifications import ToastNotification

from src.windows_toasts import InteractableWindowsToaster, WindowsToaster


def test_simple_toast():
    from src.windows_toasts import ToastText3

    simpleToast = ToastText3()

    simpleToast.SetHeadline("Hello, World!")
    simpleToast.SetFirstLine("Foobar")

    simpleToast.on_activated = lambda _: print("Toast clicked!")
    simpleToast.on_dismissed = lambda dismissedEventArgs: print(f"Toast dismissed! {dismissedEventArgs.reason}")
    simpleToast.on_failed = lambda failedEventArgs: print(f"Toast failed. {failedEventArgs.error_code}")

    WindowsToaster("Python").show_toast(simpleToast)


def test_interactable_toast(example_image_path):
    from src.windows_toasts import (
        ToastActivatedEventArgs,
        ToastButton,
        ToastButtonColour,
        ToastImage,
        ToastImageAndText2,
        ToastInputTextBox,
    )

    def notificationActivated(activatedEventArgs: ToastActivatedEventArgs):
        print(f"Clicked event args: {activatedEventArgs.arguments}")
        print(activatedEventArgs.inputs)

    newInput = ToastInputTextBox("input", "Your input:", "Write your placeholder text here!")
    firstButton = ToastButton("First", "clicked=first", image=ToastImage(example_image_path), relatedInput=newInput)
    newToast = ToastImageAndText2(actions=(firstButton,))
    newToast.SetBody("Hello, interactable world!")

    newToast.AddInput(newInput)

    newToast.AddAction(ToastButton("Second", "clicked=second", colour=ToastButtonColour.Green))
    newToast.AddAction(ToastButton("", "clicked=context", tooltip="Tooltip", inContextMenu=True))

    newToast.on_activated = notificationActivated
    InteractableWindowsToaster("Python").show_toast(newToast)


def test_audio_toast():
    from src.windows_toasts import AudioSource, ToastAudio, ToastText2

    toaster = WindowsToaster("Python")

    originalToast = ToastText2(body="Ding ding!")
    originalToast.SetAudio(ToastAudio(AudioSource.IM))

    toaster.show_toast(originalToast)

    # Branching
    silentToast = originalToast.clone()
    assert silentToast != "False EQ" and silentToast != originalToast

    silentToast.SetBody("Silence...")
    silentToast.audio.silent = True

    toaster.show_toast(silentToast)

    loopingToast = silentToast.clone()
    assert loopingToast != silentToast and loopingToast != originalToast

    loopingToast.audio.sound = "Looping.Call7"
    loopingToast.audio.looping = True
    loopingToast.audio.silent = False

    toaster.show_toast(loopingToast)


def test_errors_toast(example_image_path):
    from src.windows_toasts import (
        InvalidImageException,
        ToastButton,
        ToastDisplayImage,
        ToastImage,
        ToastImageAndText1,
        ToastInputTextBox,
        ToastText1,
    )

    textToast = ToastText1()
    with warns(UserWarning, match="has no headline, only a body"):
        textToast.SetHeadline("Hello, World!")

    displayImage = ToastDisplayImage.fromPath(example_image_path)
    with warns(UserWarning, match="Toast of type ToastText1 does not support images"):
        textToast.AddImage(displayImage)

    with warns(UserWarning, match="is a proper protocol"):
        textToast.SetLaunchAction("notanactualprotocol")

    assert len(textToast.textFields) == 1
    assert textToast.textFields[0] == "Hello, World!"

    newToast = ToastImageAndText1(body="Hello, World!")

    with raises(InvalidImageException, match="could not be found"):
        _ = ToastImage(example_image_path.with_suffix(".nonexistant"))

    newToast.AddImage(displayImage)
    newToast.AddImage(displayImage)
    for i in range(1, 6):
        if i < 4:
            newToast.AddAction(ToastButton(f"Button #{i}", str(i)))
        else:
            newToast.AddInput(ToastInputTextBox(f"Input #{i}", str(i)))

    with warns(UserWarning, match="Cannot add action 'Button 6', you've already reached"):
        newToast.AddAction(ToastButton("Button 6", str(6)))

    with warns(UserWarning, match="Cannot add input 'Input 6', you've already reached"):
        newToast.AddInput(ToastInputTextBox("Input 6", str(6)))

    with warns(UserWarning, match="The toast already has the maximum of two images"):
        newToast.AddImage(displayImage)

    with raises(InvalidImageException, match="Online images are not supported"):
        ToastImage("https://www.python.org/static/community_logos/python-powered-h-140x182.png")

    assert len(newToast.actions) + len(newToast.inputs) == 5
    for i, toastAction in enumerate(newToast.actions):
        if i < 3:
            assert newToast.actions[i] == ToastButton(f"Button #{i + 1}", str(i + 1))
        else:
            assert newToast.inputs[i] == ToastInputTextBox(f"Input #{i + 1}", str(i + 1))

    InteractableWindowsToaster("Python").show_toast(newToast)


def test_image_toast(example_image_path):
    from src.windows_toasts import ToastDisplayImage, ToastImage, ToastImageAndText4, ToastImagePosition

    toastImage = ToastImage(example_image_path)
    toastDP = ToastDisplayImage(toastImage, altText="Windows logo", position=ToastImagePosition.Hero)
    newToast = ToastImageAndText4(images=(toastDP,))

    newToast.SetHeadline("Hello, World!")
    newToast.SetFirstLine("Foo")
    newToast.SetSecondLine("Bar")

    newToast.AddImage(ToastDisplayImage.fromPath(str(example_image_path), circleCrop=False))

    InteractableWindowsToaster("Python").show_toast(newToast)


def test_custom_timestamp_toast():
    from datetime import datetime, timedelta

    from src.windows_toasts import ToastText4

    newToast = ToastText4(body="This should display as being sent an hour ago")
    newToast.SetCustomTimestamp(datetime.utcnow() - timedelta(hours=1))

    WindowsToaster("Python").show_toast(newToast)


def test_input_toast():
    from src.windows_toasts import ToastInputSelectionBox, ToastInputTextBox, ToastSelection, ToastText1

    toastTextBoxInput = ToastInputTextBox("question", "How are you today?", "Enter here!")
    newToast = ToastText1(inputs=[toastTextBoxInput])

    toastSelectionBoxInput = ToastInputSelectionBox("selection", "How about some predefined options?")
    toastSelections = (
        ToastSelection("happy", "Pretty happy"),
        ToastSelection("ok", "Meh"),
        ToastSelection("bad", "Bad"),
    )
    toastSelectionBoxInput.selections = toastSelections
    toastSelectionBoxInput.default_selection = toastSelections[1]
    newToast.AddInput(toastSelectionBoxInput)

    newBoxInput = copy.deepcopy(toastSelectionBoxInput)
    newBoxInput.default_selection = None
    newToast.AddInput(newBoxInput)

    newToast.SetBody("You. Yes, you.")

    InteractableWindowsToaster("Python").show_toast(newToast)


def test_custom_duration_toast():
    from src.windows_toasts import ToastDuration, ToastText1

    newToast = ToastText1(duration=ToastDuration.Short, body="A short toast")
    WindowsToaster("Python").show_toast(newToast)


def test_attribution_text_toast():
    from src.windows_toasts import ToastImageAndText3

    newToast = ToastImageAndText3()
    newToast.SetHeadline("Hello, World!")
    newToast.SetFirstLine("Foobar")

    toaster = WindowsToaster("Python")
    toastContent = toaster._setup_toast(newToast, False)
    toastContent.SetAttributionText("Windows-Toasts")

    toaster.toastNotifier.show(ToastNotification(toastContent.xmlDocument))


def test_scenario_toast():
    from src.windows_toasts import ToastScenario, ToastText4

    newToast = ToastText4(headline="Very important toast!", first_line="Are you ready?", second_line="Here it comes!")
    newToast.SetScenario(ToastScenario.Important)

    WindowsToaster("Python").show_toast(newToast)


def test_update_toast():
    from src.windows_toasts import ToastText1

    toaster = WindowsToaster("Python")

    newToast = ToastText1()
    newToast.SetBody("Hello, World!")

    toaster.show_toast(newToast)

    import time

    time.sleep(0.5)
    newToast.SetBody("Goodbye, World!")

    toaster.update_toast(newToast)


def test_progress_bar():
    from src.windows_toasts import ToastProgressBar, ToastText1

    progressBar = ToastProgressBar(
        "Preparing...", "Python 4 release", progress=None, progress_override="? millenniums remaining"
    )
    newToast = ToastText1(progress_bar=progressBar)

    toaster = InteractableWindowsToaster("Python", "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\cmd.exe")
    toaster.show_toast(newToast)

    # Branching
    newToast.progress_bar.progress = 0.75
    newToast.progress_bar.progress_override = None

    toaster.show_toast(newToast)


def test_scheduled_toast(pytestconfig):
    from datetime import datetime, timedelta

    from src.windows_toasts import ToastProgressBar, ToastText1

    progressBar = ToastProgressBar(
        "Preparing...", "Python 4 release", progress=0.5, progress_override="? millenniums remaining"
    )
    newToast = ToastText1(progress_bar=progressBar, body="Incoming:")

    # Branching
    clonedToast = newToast.clone()
    clonedToast.progress_bar.progress_override = None
    clonedToast.progress_bar.caption = None

    toaster = InteractableWindowsToaster("Python")
    toaster.schedule_toast(newToast, datetime.now() + timedelta(seconds=5))
    toaster.schedule_toast(clonedToast, datetime.now() + timedelta(seconds=10))

    if pytestconfig.getoption("real_run"):
        assert toaster.unschedule_toast(clonedToast)
    else:
        with warns(UserWarning, match="Toast unscheduling failed."):
            toaster.unschedule_toast(clonedToast)


def test_clear_toasts():
    toaster = InteractableWindowsToaster("Python")
    toaster.clear_scheduled_toasts()
    toaster.clear_toasts()


def test_expiration_toasts():
    from datetime import datetime, timedelta

    from src.windows_toasts import ToastText1

    expirationTime = datetime.now() + timedelta(minutes=1)
    newToast = ToastText1(body="Hello, World!", group="Test Toasts", expiration_time=expirationTime)
    WindowsToaster("Python").show_toast(newToast)


def test_protocol_launch():
    from src.windows_toasts import ToastButton, ToastText1

    newToast = ToastText1(body="Click on me to open google.com", launch_action="https://google.com")
    newToast.AddAction(ToastButton("Launch calculator", launch="calculator://"))
    InteractableWindowsToaster("Python").show_toast(newToast)
