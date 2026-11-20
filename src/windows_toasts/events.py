from __future__ import annotations

from dataclasses import dataclass

from winrt import system
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

    arguments: str | None = None
    """Arguments provided to :func:`~windows_toasts.toast.Toast.AddAction`"""
    inputs: dict | None = None
    """Inputs received when using :func:`~windows_toasts.toast.Toast.AddInput`"""

    @classmethod
    def fromWinRt(cls, eventArgs: system.Object) -> ToastActivatedEventArgs:
        activatedEventArgs = eventArgs.as_(WinRtToastActivatedEventArgs)
        receivedInputs: dict[str, str] | None = None
        try:
            receivedInputs = {k: system.unbox_string(v) for k, v in activatedEventArgs.user_input.items()}
        except OSError:
            pass

        return cls(activatedEventArgs.arguments, receivedInputs)
