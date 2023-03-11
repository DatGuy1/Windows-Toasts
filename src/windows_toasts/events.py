from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# noinspection PyProtectedMember
from winsdk import _winrt
from winsdk.windows.foundation import IPropertyValue
from winsdk.windows.ui.notifications import ToastActivatedEventArgs as WinRtToastActivatedEventArgs


@dataclass
class ToastActivatedEventArgs:
    """
    Wrapper over Windows' ToastActivatedEventArgs to fix an issue with reading user input

    :ivar arguments: Arguments provided to :func:`~windows_toasts.toast_types.Toast.AddAction`
    :ivar input: Input in field when using :func:`~windows_toasts.toast_types.Toast.SetInputField`
    """

    arguments: Optional[str] = None
    input: Optional[str] = None

    # noinspection PyProtectedMember
    @classmethod
    def fromWinRt(cls, eventArgs: _winrt.Object) -> ToastActivatedEventArgs:
        activatedEventArgs = WinRtToastActivatedEventArgs._from(eventArgs)
        try:
            textInput = IPropertyValue._from(activatedEventArgs.user_input.lookup("textBox")).get_string()
        except OSError:
            textInput = None

        return cls(activatedEventArgs.arguments, textInput)
