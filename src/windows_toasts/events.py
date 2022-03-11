from dataclasses import dataclass
from typing import Optional

from winsdk.windows.foundation import IPropertyValue
from winsdk.windows.ui.notifications import ToastActivatedEventArgs as WinRtToastActivatedEventArgs


@dataclass
class ToastActivatedEventArgs:
    arguments: Optional[str] = None
    input: Optional[str] = None

    # noinspection PyProtectedMember
    @classmethod
    def fromWinRt(cls, eventArgs):
        activatedEventArgs = WinRtToastActivatedEventArgs._from(eventArgs)
        try:
            textInput = IPropertyValue._from(activatedEventArgs.user_input.lookup("textBox")).get_string()
        except OSError:
            textInput = None

        return cls(activatedEventArgs.arguments, textInput)
