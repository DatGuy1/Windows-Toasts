from typing import Optional

# noinspection PyProtectedMember
from winsdk import _winrt

class ToastActivatedEventArgs:
    arguments: Optional[str]
    input: Optional[str]

    @classmethod
    def fromWinRt(cls, eventArgs: _winrt.Object) -> ToastActivatedEventArgs: ...
