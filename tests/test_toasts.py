from warnings import catch_warnings, simplefilter

import pytest

from src.windows_toasts import InteractableWindowsToaster, Toast, WindowsToaster


def test_simple_toast():
    simpleToast = Toast()

    simpleToast.text_fields = ["Hello, World!", "Foobar"]

    simpleToast.on_activated = lambda _: print("Toast clicked!")
    simpleToast.on_dismissed = lambda dismissedEventArgs: print(f"Toast dismissed! {dismissedEventArgs.reason}")
    simpleToast.on_failed = lambda failedEventArgs: print(f"Toast failed. {failedEventArgs.error_code}")

    WindowsToaster("Python").show_toast(simpleToast)


def test_multiline_toast():
    multilineToast = Toast(["Hello, World!", None, "Goodbye, World!"])

    WindowsToaster("Python").show_toast(multilineToast)
    InteractableWindowsToaster("Python").show_toast(multilineToast)


def test_interactable_toast(example_image_path):
    from src.windows_toasts import (
        ToastActivatedEventArgs,
        ToastButton,
        ToastButtonColour,
        ToastImage,
        ToastInputTextBox,
    )

    def notificationActivated(activatedEventArgs: ToastActivatedEventArgs):
        print(f"Clicked event args: {activatedEventArgs.arguments}")
        print(activatedEventArgs.inputs)

    newInput = ToastInputTextBox("input", "Your input:", "Write your placeholder text here!")
    firstButton = ToastButton("First", "clicked=first", image=ToastImage(example_image_path), relatedInput=newInput)
    newToast = Toast(actions=(firstButton,))
    newToast.text_fields = ["Hello, interactable world!"]

    newToast.AddInput(newInput)

    newToast.AddAction(ToastButton("Second", "clicked=second", colour=ToastButtonColour.Green))
    newToast.AddAction(ToastButton("Context", "clicked=context", tooltip="Tooltip", inContextMenu=True))

    newToast.on_activated = notificationActivated
    InteractableWindowsToaster("Python").show_toast(newToast)


def test_context_menu_button_without_content():
    from src.windows_toasts import ToastButton

    newToast = Toast(["Hello, context menu!"])
    newToast.AddAction(ToastButton("", "clicked=context", tooltip="Tooltip", inContextMenu=True))
    with pytest.raises(ValueError, match="context menu"):
        InteractableWindowsToaster("Python").show_toast(newToast)


def test_audio_toast():
    from src.windows_toasts import AudioSource, ToastAudio

    toaster = WindowsToaster("Python")

    originalToast = Toast(["Ding ding!"])
    originalToast.audio = ToastAudio(AudioSource.IM)

    toaster.show_toast(originalToast)

    # Branching
    silentToast = originalToast.clone()
    assert silentToast != "False EQ"
    assert silentToast != originalToast

    silentToast.text_fields = ["Silence..."]
    silentToast.audio.silent = True

    toaster.show_toast(silentToast)

    loopingToast = silentToast.clone()
    assert loopingToast != silentToast
    assert loopingToast != originalToast

    loopingToast.audio.sound = AudioSource.Call7
    loopingToast.audio.looping = True
    loopingToast.audio.silent = False
    loopingToast.text_fields = ["Ring, ring"]

    toaster.show_toast(loopingToast)

    # Setting the audio again replaces the previous audio instead of keeping its attributes
    from src.windows_toasts.toast_document import ToastDocument

    toastDocument = ToastDocument(originalToast)
    toastDocument.SetAudioAttributes(ToastAudio(silent=True))
    toastDocument.SetAudioAttributes(ToastAudio(AudioSource.IM))
    assert toastDocument.xmlDocument.get_xml().endswith('<audio src="ms-winsoundevent:Notification.IM"/></toast>')


def test_custom_audio_toast(example_audio_path, example_image_path):
    from src.windows_toasts import ToastAudio

    toaster = WindowsToaster("Python")

    nonExistantFile = example_audio_path.with_stem("nonexistant")
    toast = Toast(["This should pop with the default sound"], audio=ToastAudio(nonExistantFile))
    with pytest.warns(UserWarning, match="could not be found"):
        toaster.show_toast(toast)

    unsupportedFile = example_image_path
    toast.audio = ToastAudio(unsupportedFile)
    with pytest.warns(UserWarning, match=f"has unsupported extension '{example_image_path.suffix}'"):
        toaster.show_toast(toast)

    toast.audio = ToastAudio(example_audio_path)
    toast.text_fields = ["This should pop with a soft chime"]
    toaster.show_toast(toast)


def test_errors_toast(example_image_path):
    from src.windows_toasts import InvalidImageException, ToastButton, ToastDisplayImage, ToastImage, ToastInputTextBox

    textToast = Toast()
    textToast.text_fields = ["Hello, World!"]

    displayImage = ToastDisplayImage.fromPath(example_image_path)

    fakeProtocol = "notanactualprotocol"
    with pytest.warns(UserWarning, match=f"Ensure your launch action of {fakeProtocol} is of a proper protocol"):
        textToast.launch_action = fakeProtocol

    assert textToast.text_fields[0] == "Hello, World!"

    newToast = Toast(["Hello, World!"])

    with pytest.raises(InvalidImageException, match="could not be found"):
        _ = ToastImage(example_image_path.with_suffix(".nonexistant"))

    newToast.AddImage(displayImage)
    newToast.AddImage(displayImage)
    for i in range(1, 6):
        if i < 4:
            newToast.AddAction(ToastButton(f"Button #{i}", str(i)))
        else:
            newToast.AddInput(ToastInputTextBox(f"Input #{i}", str(i)))

    with pytest.warns(UserWarning, match="Cannot add action 'Button 6', you've already reached"):
        newToast.AddAction(ToastButton("Button 6", str(6)))

    with pytest.warns(UserWarning, match="Cannot add input 'Input 6', you've already reached"):
        newToast.AddInput(ToastInputTextBox("Input 6", str(6)))

    with pytest.raises(InvalidImageException, match="Online images are not supported"):
        ToastImage("https://www.python.org/static/community_logos/python-powered-h-140x182.png")

    assert len(newToast.actions) + len(newToast.inputs) == 5
    assert newToast.actions == [ToastButton(f"Button #{i}", str(i)) for i in range(1, 4)]
    assert newToast.inputs == [ToastInputTextBox(f"Input #{i}", str(i)) for i in range(4, 6)]

    InteractableWindowsToaster("Python").show_toast(newToast)


def test_image_toast(example_image_path):
    from src.windows_toasts import ToastDisplayImage, ToastImage, ToastImagePosition

    toastImage = ToastImage(example_image_path)
    toastDP = ToastDisplayImage(toastImage, altText="Python logo", position=ToastImagePosition.Hero)
    newToast = Toast(images=(toastDP,))

    newToast.text_fields = ["Hello, World!", "Foo", "Bar"]

    newToast.AddImage(ToastDisplayImage.fromPath(str(example_image_path), circleCrop=True))

    InteractableWindowsToaster("Python").show_toast(newToast)

    # WindowsToaster only shows the first image
    with pytest.warns(UserWarning, match="multiple images are not supported"):
        WindowsToaster("Python").show_toast(Toast(images=[ToastDisplayImage(toastImage)] * 2))

    with catch_warnings():
        simplefilter("error")
        WindowsToaster("Python").show_toast(Toast(["One image"], images=[ToastDisplayImage(toastImage)]))


def test_windows_toaster_warnings(example_image_path):
    from src.windows_toasts import (
        ToastButton,
        ToastDisplayImage,
        ToastImage,
        ToastImagePosition,
        ToastInputTextBox,
        ToastProgressBar,
    )

    heroImage = ToastDisplayImage(ToastImage(example_image_path), position=ToastImagePosition.Hero)
    # WindowsToaster still shows these toasts, without the parts it doesn't support
    for feature, newToast in (
        ("input fields", Toast(inputs=[ToastInputTextBox("input")])),
        ("actions", Toast(actions=[ToastButton("Button", "button")])),
        ("progress bars", Toast(progress_bar=ToastProgressBar("Preparing..."))),
        ("hero placements", Toast(images=[heroImage])),
    ):
        with pytest.warns(UserWarning, match=f"^{feature} are not supported in WindowsToaster"):
            WindowsToaster("Python").show_toast(newToast)


def test_custom_timestamp_toast():
    from datetime import UTC, datetime, timedelta

    newToast = Toast(["This should display as being sent an hour ago"])
    newToast.timestamp = datetime.now(UTC) - timedelta(hours=1)

    WindowsToaster("Python").show_toast(newToast)


def test_input_toast():
    import copy

    from src.windows_toasts import ToastInputSelectionBox, ToastInputTextBox, ToastSelection

    toastTextBoxInput = ToastInputTextBox("question", "How are you today?", "Enter here!")
    newToast = Toast(inputs=[toastTextBoxInput])

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

    newToast.text_fields = ["You. Yes, you."]

    InteractableWindowsToaster("Python").show_toast(newToast)


def test_custom_duration_toast():
    from src.windows_toasts import ToastDuration

    newToast = Toast(["A short toast"], duration=ToastDuration.Short)
    WindowsToaster("Python").show_toast(newToast)


def test_attribution_text_toast():
    newToast = Toast(["Incoming Message", "How are you?"])
    newToast.attribution_text = "Via FakeMessenger"

    InteractableWindowsToaster("Python").show_toast(newToast)


def test_scenario_toast():
    from src.windows_toasts import ToastScenario

    newToast = Toast(["Very important toast!", "Are you ready?", "Here it comes!"])
    newToast.scenario = ToastScenario.Important

    WindowsToaster("Python").show_toast(newToast)


def test_update_toast():
    toaster = WindowsToaster("Python")

    newToast = Toast()
    newToast.text_fields = ["Hello, World!"]

    toaster.show_toast(newToast)

    import time

    time.sleep(0.5)
    newToast.text_fields = ["Goodbye, World!"]

    toaster.update_toast(newToast)


def test_progress_bar():
    from src.windows_toasts import ToastProgressBar

    progressBar = ToastProgressBar(
        "Preparing...", "Python 4 release", progress=None, progress_override="? millenniums remaining"
    )
    newToast = Toast(progress_bar=progressBar)

    toaster = InteractableWindowsToaster("Python", "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\cmd.exe")
    toaster.show_toast(newToast)

    # Branching
    newToast.progress_bar.progress = 0.75
    newToast.progress_bar.progress_override = None

    toaster.show_toast(newToast)


def test_indeterminate_progress_bar_without_override():
    from src.windows_toasts import ToastProgressBar
    from src.windows_toasts.toasters import _build_adaptable_data

    newToast = Toast(progress_bar=ToastProgressBar("Preparing...", progress=None))
    values = _build_adaptable_data(newToast).values
    assert values["progress"] == "indeterminate"
    assert values["progress_override"] == ""


def test_expires_on_reboot():
    from datetime import datetime, timedelta

    from winrt.windows.ui.notifications import ScheduledToastNotification, ToastNotification

    from src.windows_toasts.toasters import _build_toast_notification

    newToast = Toast(["Gone after a restart"], expires_on_reboot=True)
    toaster = InteractableWindowsToaster("Python")
    toaster.show_toast(newToast)

    xmlDocument = toaster._setup_toast(newToast, True).xmlDocument
    assert _build_toast_notification(newToast, ToastNotification(xmlDocument)).expires_on_reboot
    assert not _build_toast_notification(Toast(), ToastNotification(xmlDocument)).expires_on_reboot

    # Scheduled toasts don't have the property, so building one must not try to set it
    scheduled = ScheduledToastNotification(xmlDocument, datetime.now() + timedelta(minutes=1))
    _build_toast_notification(newToast, scheduled)


def test_text_box_default_input():
    from src.windows_toasts import ToastInputTextBox

    toaster = InteractableWindowsToaster("Python")

    prefilledToast = Toast(["Prefilled"], inputs=[ToastInputTextBox("reply", "Reply", "Placeholder", "Prefilled")])
    toaster.show_toast(prefilledToast)
    assert 'defaultInput="Prefilled"' in toaster._setup_toast(prefilledToast, True).xmlDocument.get_xml()

    emptyToast = Toast(["Empty"], inputs=[ToastInputTextBox("reply", "Reply", "Placeholder")])
    assert "defaultInput" not in toaster._setup_toast(emptyToast, True).xmlDocument.get_xml()


def test_header():
    from src.windows_toasts import ToastHeader

    header = ToastHeader("Reminders")
    assert header.header_id == "Reminders"
    firstToast = Toast(["Drink some water"], header=header)
    secondToast = Toast(["Stretch your legs"], header=header)

    toaster = InteractableWindowsToaster("Python")
    toaster.show_toast(firstToast)
    toaster.show_toast(secondToast)
    WindowsToaster("Python").show_toast(Toast(["Legacy template"], header=header))

    xmlDocument = toaster._setup_toast(firstToast, True).xmlDocument
    headerNode = xmlDocument.get_elements_by_tag_name("toast").item(0).first_child
    assert headerNode.node_name == "header"
    assert headerNode.get_xml() == '<header id="Reminders" title="Reminders" arguments=""/>'

    launchHeader = ToastHeader("Today's reminders", "reminders", launch="https://example.com/reminders")
    launchToast = Toast(["Water the plants"], header=launchHeader)
    assert (
        '<header id="reminders" title="Today\'s reminders" activationType="protocol" '
        'arguments="https://example.com/reminders"/>'
    ) in toaster._setup_toast(launchToast, True).xmlDocument.get_xml()
    assert "<header" not in toaster._setup_toast(Toast(["No header"]), True).xmlDocument.get_xml()


def test_groups(example_image_path):
    from datetime import datetime, timedelta

    from src.windows_toasts import (
        ToastGroup,
        ToastGroupImage,
        ToastImage,
        ToastImageAlign,
        ToastSubgroup,
        ToastText,
        ToastTextAlign,
        ToastTextStacking,
        ToastTextStyle,
    )

    styledText = ToastText(
        "Styled", ToastTextStyle.TitleSubtle, ToastTextAlign.Center, wrap=True, max_lines=2, min_lines=1
    )
    image = ToastGroupImage(
        ToastImage(example_image_path), "Alt", circle_crop=True, remove_margin=True, align=ToastImageAlign.Right
    )
    group = ToastGroup(
        [
            ToastSubgroup([ToastText("Plain"), styledText]),
            ToastSubgroup([image], weight=2, text_stacking=ToastTextStacking.Bottom),
        ]
    )
    newToast = Toast(["Groups"], groups=[group])

    toaster = InteractableWindowsToaster("Python")
    toaster.show_toast(newToast)
    toaster.schedule_toast(newToast, datetime.now() + timedelta(seconds=10))

    xml = toaster._setup_toast(newToast, True).xmlDocument.get_xml()
    assert (
        "<group><subgroup><text>Plain</text>"
        '<text hint-style="titleSubtle" hint-align="center" hint-wrap="true" hint-maxLines="2" hint-minLines="1">'
        "Styled</text></subgroup>"
        f'<subgroup hint-weight="2" hint-textStacking="bottom"><image src="{image.image.path}" alt="Alt" '
        'hint-crop="circle" hint-removeMargin="true" hint-align="right"/></subgroup></group>'
    ) in xml

    plainImage = ToastGroupImage(ToastImage(example_image_path))
    plainImageToast = Toast(["Plain image"], groups=[ToastGroup([ToastSubgroup([plainImage])])])
    assert f'<subgroup><image src="{plainImage.image.path}"/></subgroup>' in (
        toaster._setup_toast(plainImageToast, True).xmlDocument.get_xml()
    )

    with pytest.warns(UserWarning, match="groups are not supported"):
        WindowsToaster("Python").show_toast(newToast)
    assert "<group" not in WindowsToaster("Python")._setup_toast(newToast, True).xmlDocument.get_xml()


def test_positional_arguments_deprecated():
    from src.windows_toasts import AudioSource, ToastAudio, ToastDuration

    audio = ToastAudio(AudioSource.IM)

    with pytest.warns(DeprecationWarning, match="audio, duration as keyword arguments"):
        legacyToast = Toast(["Legacy"], audio, ToastDuration.Long)
    assert legacyToast.audio is audio
    assert legacyToast.duration is ToastDuration.Long

    with pytest.raises(TypeError, match="multiple values for argument 'audio'"):
        Toast(["Legacy"], audio, audio=audio)

    with pytest.raises(TypeError, match="at most 17 positional arguments"):
        Toast(["Legacy"], *([None] * 17))


def test_notification_enums_match_winrt():
    from winrt.windows.ui.notifications import (
        NotificationSetting as WinRtNotificationSetting,
        ToastNotificationMode as WinRtToastNotificationMode,
    )

    from src.windows_toasts import NotificationSetting, ToastNotificationMode

    for ours, theirs in (
        (NotificationSetting, WinRtNotificationSetting),
        (ToastNotificationMode, WinRtToastNotificationMode),
    ):
        assert [(member.name.replace("_", "").lower(), member.value) for member in ours] == [
            (member.name.replace("_", "").lower(), int(member)) for member in theirs
        ]
        # Plain Enums so that a zero value, like NotificationSetting.Enabled, isn't falsy
        assert all(member for member in ours)

    # A value a newer Windows might return becomes a member instead of raising
    unknown = NotificationSetting(99)
    assert unknown.value == 99
    assert unknown.name == "99"
    assert NotificationSetting(99) is unknown
    assert unknown not in list(NotificationSetting)
    with pytest.raises(ValueError, match="is not a valid NotificationSetting"):
        NotificationSetting("Enabled")


def test_notification_setting():
    import uuid
    from unittest.mock import Mock, PropertyMock

    from winrt.windows.ui.notifications import NotificationSetting as WinRtNotificationSetting

    from src.windows_toasts import NotificationSetting

    # Windows has no settings for an AUMID until it shows its first toast
    assert WindowsToaster(f"WindowsToasts.Tests.{uuid.uuid4()}").notification_setting is None

    toaster = InteractableWindowsToaster("Python")
    toaster.toastNotifier = Mock(setting=WinRtNotificationSetting.DISABLED_FOR_USER)
    assert toaster.notification_setting is NotificationSetting.DisabledForUser

    # Any other error still propagates
    toaster.toastNotifier = Mock()
    type(toaster.toastNotifier).setting = PropertyMock(side_effect=OSError(0, "Access is denied", None, 5))
    with pytest.raises(OSError, match="Access is denied"):
        _ = toaster.notification_setting


def test_notification_mode():
    from src.windows_toasts import ToastNotificationMode

    assert isinstance(WindowsToaster("Python").notification_mode, ToastNotificationMode)


def test_dismissal_reason():
    from winrt.windows.ui.notifications import ToastDismissalReason as WinRtToastDismissalReason

    from src.windows_toasts import ToastDismissalReason

    assert [(member.name.lower(), member.value) for member in ToastDismissalReason] == [
        (member.name.replace("_", "").lower(), int(member)) for member in WinRtToastDismissalReason
    ]
    assert ToastDismissalReason.UserCanceled == WinRtToastDismissalReason.USER_CANCELED == 0

    for old, new in (
        ("USER_CANCELED", ToastDismissalReason.UserCanceled),
        ("APPLICATION_HIDDEN", ToastDismissalReason.ApplicationHidden),
        ("TIMED_OUT", ToastDismissalReason.TimedOut),
    ):
        with pytest.warns(DeprecationWarning, match=f"ToastDismissalReason.{old} is deprecated") as record:
            assert getattr(ToastDismissalReason, old) is new
        assert record[0].filename == __file__
        assert old not in ToastDismissalReason.__members__

    unknown = ToastDismissalReason(7)
    assert unknown == 7
    assert unknown.name == "7"
    assert ToastDismissalReason(7) is unknown


def test_event_args_from_winrt():
    from unittest.mock import Mock

    from winrt.windows.foundation import HResult
    from winrt.windows.ui.notifications import ToastDismissalReason as WinRtToastDismissalReason

    from src.windows_toasts import ToastDismissalReason, ToastDismissedEventArgs, ToastFailedEventArgs

    dismissed = ToastDismissedEventArgs.fromWinRt(Mock(reason=WinRtToastDismissalReason.TIMED_OUT))
    assert dismissed.reason is ToastDismissalReason.TimedOut

    failed = ToastFailedEventArgs.fromWinRt(Mock(error_code=HResult(-2147024891)))
    assert failed.error_code == -2147024891


def test_scheduled_toast(pytestconfig):
    from datetime import datetime, timedelta
    from unittest.mock import patch

    from winrt.windows.ui.notifications import ToastNotifier

    from src.windows_toasts import ToastNotFoundError, ToastProgressBar

    progressBar = ToastProgressBar(
        "Preparing...", "Python 4 release", progress=0.5, progress_override="? millenniums remaining"
    )
    newToast = Toast(progress_bar=progressBar, text_fields=["Incoming:"])

    # Branching
    clonedToast = newToast.clone()
    clonedToast.progress_bar.progress_override = None
    clonedToast.progress_bar.caption = None

    toaster = InteractableWindowsToaster("Python")
    toaster.schedule_toast(newToast, datetime.now() + timedelta(seconds=5))
    toaster.schedule_toast(clonedToast, datetime.now() + timedelta(seconds=10))

    if pytestconfig.getoption("real_run"):
        toaster.unschedule_toast(clonedToast)
    else:
        with pytest.raises(ToastNotFoundError, match=r"Toast unscheduling failed\."):
            toaster.unschedule_toast(clonedToast)

        scheduledToasts = [call.args[0] for call in ToastNotifier.add_to_schedule.call_args_list]
        with (
            patch(
                "winrt.windows.ui.notifications.ToastNotifier.get_scheduled_toast_notifications",
                return_value=scheduledToasts,
            ),
            patch("winrt.windows.ui.notifications.ToastNotifier.remove_from_schedule") as removeFromSchedule,
        ):
            toaster.unschedule_toast(clonedToast)

        removeFromSchedule.assert_called_once()
        assert removeFromSchedule.call_args.args[0].tag == clonedToast.tag


def test_legacy_scheduled_toast():
    from datetime import datetime, timedelta

    toaster = WindowsToaster("Python")
    newToast = Toast(["Later", None])
    toaster.schedule_toast(newToast, datetime.now() + timedelta(seconds=10))

    # Scheduled toasts can't be bound to data, so their text is written in directly
    xml = toaster._setup_toast(newToast, False).xmlDocument.get_xml()
    assert '<text id="1">Later</text><text id="2"></text>' in xml


def test_clear_toasts():
    from unittest.mock import Mock, patch

    toaster = InteractableWindowsToaster("Python")
    toaster.clear_scheduled_toasts()
    toaster.clear_toasts()

    scheduledToasts = [Mock(), Mock()]
    with (
        patch(
            "winrt.windows.ui.notifications.ToastNotifier.get_scheduled_toast_notifications",
            return_value=scheduledToasts,
        ),
        patch("winrt.windows.ui.notifications.ToastNotifier.remove_from_schedule") as removeFromSchedule,
    ):
        toaster.clear_scheduled_toasts()

    assert [call.args[0] for call in removeFromSchedule.call_args_list] == scheduledToasts


def test_expiration_toasts():
    from datetime import datetime, timedelta

    expirationTime = datetime.now() + timedelta(minutes=1)
    newToast = Toast(["Hello, World!"], group="Test Toasts", expiration_time=expirationTime)
    WindowsToaster("Python").show_toast(newToast)


def test_protocol_launch():
    from src.windows_toasts import ToastButton

    newToast = Toast(["Click on me to open google.com"], launch_action="https://google.com")
    newToast.AddAction(ToastButton("Launch calculator", launch="calculator://"))
    InteractableWindowsToaster("Python").show_toast(newToast)


def test_system_toast():
    from src.windows_toasts import ToastInputSelectionBox, ToastSelection, ToastSystemButton, ToastSystemButtonAction

    newToast = Toast(["Reminder", "It's time to stretch!"])

    selections = (ToastSelection("1", "1 minute"), ToastSelection("2", "2 minutes"), ToastSelection("5", "5 minutes"))
    selectionBox = ToastInputSelectionBox(
        "snoozeBox", caption="Snooze duration", selections=selections, default_selection=selections[0]
    )
    newToast.AddInput(selectionBox)

    snoozeButton = ToastSystemButton(ToastSystemButtonAction.Snooze, "Remind Me Later", relatedInput=selectionBox)
    dismissBox = ToastSystemButton(ToastSystemButtonAction.Dismiss)
    newToast.AddAction(snoozeButton)
    newToast.AddAction(dismissBox)

    InteractableWindowsToaster("Python").show_toast(newToast)


def test_unsupported_types():
    from types import SimpleNamespace

    from src.windows_toasts import ToastGroup, ToastSubgroup, ToastSystemButton, ToastSystemButtonAction

    # Nothing stops these from being given a type they don't support, so the toast raises instead of being incomplete
    invalidButton = ToastSystemButton(ToastSystemButtonAction.Snooze)
    invalidButton.action = 0
    invalidToasts = (
        Toast(["Invalid system button"], actions=[invalidButton]),
        Toast(["Invalid action"], actions=[SimpleNamespace(content="Not a button")]),
        Toast(["Invalid input"], inputs=[SimpleNamespace(input_id="notAnInput", caption="Not an input")]),
        Toast(["Invalid group content"], groups=[ToastGroup([ToastSubgroup(["Not text or an image"])])]),
    )

    toaster = InteractableWindowsToaster("Python")
    for invalidToast in invalidToasts:
        with pytest.raises(AssertionError, match="Expected code to be unreachable"):
            toaster.show_toast(invalidToast)


def test_remove_toast():
    toaster = WindowsToaster("Python")
    newToast = Toast(["Disappearing act"])

    toaster.show_toast(newToast)

    import time

    time.sleep(0.5)

    toaster.remove_toast(newToast)


def test_toast_tag():
    defaultToast = Toast()
    assert len(defaultToast.tag) == 36
    assert Toast(tag="reminder").tag == "reminder"
    assert Toast(tag="a" * 63, group="b" * 63).group == "b" * 63

    # Windows uses the tag as the group when there's none
    assert Toast(tag="reminder") == Toast(tag="reminder", group="reminder")
    assert Toast(tag="reminder", group="a") != Toast(tag="reminder", group="b")
    assert Toast(tag="reminder") != Toast(tag="reminder", group="a")

    for invalid in ("", "a" * 64, "🐍" * 32):
        with pytest.raises(ValueError, match="1 to 63 characters"):
            Toast(tag=invalid)
        with pytest.raises(ValueError, match="1 to 63 characters"):
            defaultToast.group = invalid


def test_action_center_toasts(pytestconfig):
    import time
    from unittest.mock import patch

    from winrt.windows.ui.notifications import ToastNotifier

    from src.windows_toasts import ToastProgressBar

    toaster = InteractableWindowsToaster("Python")
    progressBar = ToastProgressBar("Downloading", "Python 4", progress=0.25)
    toaster.show_toast(
        Toast(["Hello", None, "World"], tag="action-center-test", progress_bar=progressBar, suppress_popup=True)
    )
    toaster.show_toast(
        Toast(
            ["Grouped"],
            tag="action-center-test-2",
            group="action-center-group",
            progress_bar=ToastProgressBar("Waiting", progress=None),
            suppress_popup=True,
        )
    )

    realRun = pytestconfig.getoption("real_run")
    if realRun:
        time.sleep(0.5)
        listedToasts = toaster.get_action_center_toasts()
    else:
        # show is mocked, so hand what it was given to the history instead
        shownToasts = [call.args[0] for call in ToastNotifier.show.call_args_list]
        with patch("winrt.windows.ui.notifications.ToastNotificationHistory.get_history", return_value=shownToasts):
            listedToasts = toaster.get_action_center_toasts()

    toasts = {toast.tag: toast for toast in listedToasts}
    first, second = toasts["action-center-test"], toasts["action-center-test-2"]
    assert first.group is None
    assert first.text_fields == ("Hello", None, "World")
    assert first.progress_bar == progressBar
    # Windows sets a default expiration time when it shows the toast
    assert (first.expiration_time is not None) == realRun
    assert second.group == "action-center-group"
    assert second.progress_bar == ToastProgressBar("Waiting", progress=None)

    toaster.remove_toast(Toast(tag=first.tag, group=first.group))
    toaster.remove_toast(Toast(tag=second.tag, group=second.group))
    if realRun:
        time.sleep(0.5)
        assert not {first.tag, second.tag} & {toast.tag for toast in toaster.get_action_center_toasts()}


def test_action_center_toasts_unreadable():
    from unittest.mock import Mock, PropertyMock, patch

    unreadableToast = Mock()
    type(unreadableToast).tag = PropertyMock(side_effect=OSError)
    with patch("winrt.windows.ui.notifications.ToastNotificationHistory.get_history", return_value=[unreadableToast]):
        assert InteractableWindowsToaster("Python").get_action_center_toasts() == []


def test_remove_toast_group():
    import time

    from src.windows_toasts import ToastActivatedEventArgs

    toaster = WindowsToaster("Python")

    toast1 = Toast(["A bigger disappearing act"], group="begone")
    toast2 = Toast(["Click me to shazam!"], group="begone")

    toast2.on_activated = lambda _: toaster.remove_toast_group("begone")

    toaster.show_toast(toast1)
    toaster.show_toast(toast2)

    # If it hasn't been activated, remove it ourselves
    time.sleep(1)

    toast2.on_activated(ToastActivatedEventArgs())
