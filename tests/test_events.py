from unittest.mock import Mock, PropertyMock

from winrt import system
from winrt.windows.foundation.collections import ValueSet
from winrt.windows.ui.notifications import ToastActivatedEventArgs as WinRtToastActivatedEventArgs

from src.windows_toasts import ToastActivatedEventArgs


def _make_event_args(arguments: str, userInput: ValueSet) -> tuple[Mock, Mock]:
    activatedEventArgs = Mock(spec=WinRtToastActivatedEventArgs)
    activatedEventArgs.arguments = arguments
    activatedEventArgs.user_input = userInput

    # What Activated actually passes the handler before it is cast
    eventArgs = Mock(spec=system.Object)
    eventArgs.as_.return_value = activatedEventArgs

    return eventArgs, activatedEventArgs


def test_activated_event_args_from_winrt():
    userInput = ValueSet()
    userInput.insert("textBox", system.box_string("World, Hello!"))
    userInput.insert("selection", system.box_string("option2"))

    eventArgs, _ = _make_event_args("test=yes", userInput)
    parsedArgs = ToastActivatedEventArgs.fromWinRt(eventArgs)

    eventArgs.as_.assert_called_once_with(WinRtToastActivatedEventArgs)
    assert parsedArgs == ToastActivatedEventArgs("test=yes", {"textBox": "World, Hello!", "selection": "option2"})


def test_activated_event_args_without_inputs():
    eventArgs, _ = _make_event_args("clicked=first", ValueSet())

    assert ToastActivatedEventArgs.fromWinRt(eventArgs) == ToastActivatedEventArgs("clicked=first", {})


def test_activated_event_args_unreadable_inputs():
    eventArgs, activatedEventArgs = _make_event_args("clicked=first", ValueSet())
    type(activatedEventArgs).user_input = PropertyMock(side_effect=OSError)

    assert ToastActivatedEventArgs.fromWinRt(eventArgs) == ToastActivatedEventArgs("clicked=first", None)
