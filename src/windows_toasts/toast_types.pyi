import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, ClassVar, List, Literal, Optional, Tuple, Union
from winsdk.windows.ui.notifications import (ToastDismissedEventArgs, ToastFailedEventArgs, ToastTemplateType)
from .events import ToastActivatedEventArgs
from .toast_audio import ToastAudio

class ToastDuration(Enum):
    Default: str
    Short: str
    Long: str

class Toast:
    ToastType: ClassVar[ToastTemplateType]
    HasImage: ClassVar[bool]
    audio: Optional[ToastAudio]
    actions: List[Tuple[str, str]]
    duration: Literal[ToastDuration.Default, ToastDuration.Long, ToastDuration.Short]
    imagePath: Optional[Path]
    textFields: List[str]
    textInputPlaceholder: Optional[str]
    timestamp: Optional[datetime.datetime]
    on_activated: Optional[Callable[[ToastActivatedEventArgs], None]]
    on_dismissed: Optional[Callable[[ToastDismissedEventArgs], None]]
    on_failed: Optional[Callable[[ToastFailedEventArgs], None]]
    def __init__(self) -> None: ...
    def AddAction(self, actionName: str, actionArguments: str): ...
    def SetHeadline(self, headlineText: str) -> None: ...
    def SetBody(self, bodyText: str) -> None: ...
    def SetFirstLine(self, lineText: str) -> None: ...
    def SetSecondLine(self, lineText: str) -> None: ...
    def SetImage(self, imagePath: Union[str, Path]) -> None: ...
    def SetInputField(self, placeholderText: str) -> None: ...
    def SetCustomTimestamp(self, notificationTime: datetime.datetime) -> None: ...

class ToastText1(Toast):
    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_TEXT01]]
    def __init__(self) -> None: ...

class ToastText2(Toast):
    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_TEXT02]]
    def __init__(self) -> None: ...

class ToastText3(Toast):
    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_TEXT03]]
    def __init__(self) -> None: ...

class ToastText4(Toast):
    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_TEXT04]]
    def __init__(self) -> None: ...

class ToastImageAndText1(Toast):
    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_IMAGE_AND_TEXT01]]
    HasImage: ClassVar[Literal[True]]
    def __init__(self) -> None: ...

class ToastImageAndText2(Toast):
    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_IMAGE_AND_TEXT02]]
    HasImage: ClassVar[Literal[True]]
    def __init__(self) -> None: ...

class ToastImageAndText3(Toast):
    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_IMAGE_AND_TEXT03]]
    HasImage: ClassVar[Literal[True]]
    def __init__(self) -> None: ...

class ToastImageAndText4(Toast):
    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_IMAGE_AND_TEXT04]]
    HasImage: ClassVar[Literal[True]]
    def __init__(self) -> None: ...
