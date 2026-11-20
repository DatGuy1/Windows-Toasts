from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import TypeVar

from winrt import system
from winrt.windows.ui.notifications import (
    ToastActivatedEventArgs as WinRtToastActivatedEventArgs,
    ToastDismissedEventArgs as WinRtToastDismissedEventArgs,
    ToastFailedEventArgs as WinRtToastFailedEventArgs,
)

from .wrappers import _WindowsEnum

EnumT = TypeVar("EnumT", bound=Enum)


class _DeprecatedAlias:
    """
    An old name for an enum member, which still works but warns. Enums don't turn descriptors into members, so the old
    name is left out of iteration and ``__members__``
    """

    def __init__(self, memberName: str):
        self.memberName = memberName
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: object, owner: type[EnumT]) -> EnumT:
        warnings.warn(
            f"{owner.__name__}.{self.name} is deprecated, use {owner.__name__}.{self.memberName} instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return owner[self.memberName]


@dataclass
class ToastActivatedEventArgs:
    """
    Passed to :attr:`~windows_toasts.toast.Toast.on_activated` when the toast or one of its buttons is clicked
    """

    arguments: str | None = None
    """Arguments provided to :func:`~windows_toasts.toast.Toast.AddAction`"""
    inputs: dict | None = None
    """Inputs received when using :func:`~windows_toasts.toast.Toast.AddInput`"""

    @classmethod
    def fromWinRt(cls, eventArgs: system.Object) -> ToastActivatedEventArgs:
        activatedEventArgs = eventArgs.as_(WinRtToastActivatedEventArgs)
        receivedInputs: dict[str, str] | None = None
        # Windows gives the inputs as boxed values, so they're unboxed into plain strings here
        try:
            receivedInputs = {k: system.unbox_string(v) for k, v in activatedEventArgs.user_input.items()}
        except OSError:
            pass

        return cls(activatedEventArgs.arguments, receivedInputs)


class ToastDismissalReason(IntEnum, _WindowsEnum):
    """
    Why a toast was dismissed. An IntEnum, like the Windows enum it replaced, so it still equals Windows' values
    """

    UserCanceled = 0
    """The user dismissed the toast"""
    ApplicationHidden = 1
    """The application hid the toast"""
    TimedOut = 2
    """The toast was shown for the maximum allowed time and faded out"""

    # The names of the Windows enum this replaced
    USER_CANCELED = _DeprecatedAlias("UserCanceled")
    APPLICATION_HIDDEN = _DeprecatedAlias("ApplicationHidden")
    TIMED_OUT = _DeprecatedAlias("TimedOut")


@dataclass
class ToastDismissedEventArgs:
    """
    Passed to :attr:`~windows_toasts.toast.Toast.on_dismissed` when a toast is dismissed
    """

    reason: ToastDismissalReason
    """Why the toast was dismissed"""

    @classmethod
    def fromWinRt(cls, eventArgs: WinRtToastDismissedEventArgs) -> ToastDismissedEventArgs:
        return cls(ToastDismissalReason(eventArgs.reason))


@dataclass
class ToastFailedEventArgs:
    """
    Passed to :attr:`~windows_toasts.toast.Toast.on_failed` when a toast fails to show
    """

    error_code: int
    """The HRESULT error code Windows gave, as a signed integer"""

    @classmethod
    def fromWinRt(cls, eventArgs: WinRtToastFailedEventArgs) -> ToastFailedEventArgs:
        # pywinrt's HResult is an int, and passing it on as is keeps its deprecated .value working
        return cls(eventArgs.error_code)
