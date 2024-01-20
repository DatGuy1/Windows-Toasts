from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from winrt import system
from winrt.windows.foundation import IPropertyValue
from winrt.windows.ui.notifications import (  # noqa: F401
    ToastActivatedEventArgs as WinRtToastActivatedEventArgs,
    ToastDismissalReason,
    ToastDismissedEventArgs,
    ToastFailedEventArgs,
)


@dataclass
class ToastActivatedEventArgs:
    """
    Wrapper over Windows' ToastActivatedEventArgs to fix an issue with reading user input
    """

    arguments: Optional[str] = None
    """Arguments provided to :func:`~windows_toasts.toast.Toast.AddAction`"""
    inputs: Optional[dict] = None
    """Inputs received when using :func:`~windows_toasts.toast.Toast.AddInput`"""

    # noinspection PyProtectedMember
    @classmethod
    def fromWinRt(cls, eventArgs: system.Object) -> ToastActivatedEventArgs:
        activatedEventArgs = WinRtToastActivatedEventArgs._from(eventArgs)
        receivedInputs: Optional[Dict[str, str]] = None
        try:
            receivedInputs = {k: IPropertyValue._from(v).get_string() for k, v in activatedEventArgs.user_input.items()}
        except OSError:
            pass

        return cls(activatedEventArgs.arguments, receivedInputs)
