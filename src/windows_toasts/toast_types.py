import datetime
import warnings
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Callable, ClassVar, List, Literal, Optional, Tuple, Union
from urllib.parse import urlparse

from winsdk.windows.ui.notifications import ToastDismissedEventArgs, ToastFailedEventArgs, ToastTemplateType

from .events import ToastActivatedEventArgs
from .toast_audio import ToastAudio


class ToastDuration(Enum):
    """
    Possible values for duration to display toast for
    """

    Default: str = "Default"
    Short: str = "short"
    Long: str = "long"


class Toast:
    """
    Base class for a toast. Should not be directly created

    :ivar audio: Audio configuration
    :vartype audio: Optional[ToastAudio]
    :ivar actions: List of buttons to include. Implemented through :func:`AddAction`
    :ivar duration: :class:`ToastDuration`, be it the default, short, or long
    :ivar imagePath: See :func:`SetImage`
    :ivar textFields: Various text fields (dependant on subclass)
    :ivar textInputPlaceholder: Placeholder for a text input box
    :ivar timestamp: See :func:`SetCustomTimestamp`
    :ivar on_activated: Callable to execute when the toast is clicked if basic, or a button is clicked if interactable
    :ivar on_dismissed: Callable to execute when the toast is dismissed (X is clicked or times out) if interactable
    :ivar on_failed: Callable to execute when the toast fails to display
    """

    audio: Optional[ToastAudio]
    actions: List[Tuple[str, str]]
    duration: Literal[ToastDuration.Default, ToastDuration.Long, ToastDuration.Short]
    imagePath: Optional[str]
    textFields: List[str]
    textInputPlaceholder: Optional[str]
    timestamp: Optional[datetime.datetime]
    on_activated: Optional[Callable[[ToastActivatedEventArgs], None]]
    on_dismissed: Optional[Callable[[ToastDismissedEventArgs], None]]
    on_failed: Optional[Callable[[ToastFailedEventArgs], None]]
    ToastType: ClassVar[ToastTemplateType] = None
    HasImage: ClassVar[bool] = False

    def __init__(self) -> None:
        self.audio = None
        self.actions = []
        self.duration = ToastDuration.Default
        self.imagePath = None
        self.textFields = []
        self.textInputPlaceholder = None
        self.timestamp = None

        self.on_activated = None
        self.on_dismissed = None
        self.on_failed = None

    def AddAction(self, actionName: str, actionArguments: str):
        """
        Add an action to the action list. For example, if you're setting up a reminder,
        you would use 'action=remindlater&date=2020-01-20' as arguments. Maximum of five.

        :param actionName: Value that will be displayed on the button
        :type actionName: str
        :param actionArguments: Arguments that will be available in the callback
        :type actionArguments: str
        """
        if len(self.actions) >= 5:
            warnings.warn("Cannot add any more actions, you've already reached five")
            return

        self.actions.append((actionName, actionArguments))

    def SetHeadline(self, headlineText: str) -> None:
        """
        Sets the headline (top line) for the toast. Warns to use SetBody if toast has only one line
        """
        if len(self.textFields) < 2:
            warnings.warn(f"Toast of type {self.__class__.__name__} has no headline, only a body")

        self.textFields[0] = headlineText

    def SetBody(self, bodyText: str) -> None:
        """
        Sets the text that will be displayed in the body of a single-lined toast
        """
        if len(self.textFields) == 1:
            self.textFields[0] = bodyText
        else:
            self.SetFirstLine(bodyText)

    def SetFirstLine(self, lineText: str) -> None:
        """
        Sets the text that will be displayed in the first line (not the headline) of a multi-lined toast
        """
        self.textFields[1] = lineText

    def SetSecondLine(self, lineText: str) -> None:
        """
        Sets the text that will be displayed in the second line of a two-lined (plus headline) toast
        """
        self.textFields[2] = lineText

    def SetImage(self, imagePath: Union[str, PathLike]) -> None:
        """
        Sets the image that will be displayed as the icon of the toast. Only works for ToastImageAndText classes

        :param imagePath: The path to an image, be it a file or online (max 3 MB)
        """
        if not self.HasImage:
            warnings.warn(f"Toast of type {self.__class__.__name__} does not support images. This will not work.")
            return

        if isinstance(imagePath, str) and urlparse(imagePath).scheme in ("http", "https"):
            self.imagePath = imagePath
            return
        elif not isinstance(imagePath, Path):
            imagePath = Path(imagePath)

        self.imagePath = imagePath.as_uri()

    def SetInputField(self, placeholderText: str) -> None:
        """
        Adds an input field to the notification. It will be supplied as user_input of type ValueSet in on_activated

        :param placeholderText: Placeholder text to display the the input field
        :type placeholderText: str
        """
        self.textInputPlaceholder = placeholderText

    def SetCustomTimestamp(self, notificationTime: datetime.datetime) -> None:
        """
        Sets a custom notification timestamp. If you don't provide a custom timestamp,
        Windows uses the time that your notification was sent
        """
        self.timestamp = notificationTime


class ToastText1(Toast):
    """
    A single string wrapped across a maximum of three lines of text
    """

    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_TEXT01]] = ToastTemplateType.TOAST_TEXT01

    def __init__(self) -> None:
        super().__init__()
        self.textFields = [""]


class ToastText2(Toast):
    """
    One string of bold text on the first line, one string of regular text wrapped across the second and third lines
    """

    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_TEXT02]] = ToastTemplateType.TOAST_TEXT02

    def __init__(self) -> None:
        super().__init__()
        self.textFields = ["", ""]


class ToastText3(Toast):
    """
    One string of bold text wrapped across the first and second lines, one string of regular text on the third line
    """

    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_TEXT03]] = ToastTemplateType.TOAST_TEXT03

    def __init__(self) -> None:
        super().__init__()
        self.textFields = ["", ""]


class ToastText4(Toast):
    """
    One string of bold text on the first line, one string of regular text on the second line,
    one string of regular text on the third line
    """

    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_TEXT04]] = ToastTemplateType.TOAST_TEXT04

    def __init__(self) -> None:
        super().__init__()
        self.textFields = ["", "", ""]


# noinspection DuplicatedCode
class ToastImageAndText1(Toast):
    """
    An image and a single string wrapped across a maximum of three lines of text
    """

    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_IMAGE_AND_TEXT01]] = ToastTemplateType.TOAST_IMAGE_AND_TEXT01
    HasImage: ClassVar[Literal[True]] = True

    def __init__(self) -> None:
        super().__init__()
        self.textFields = [""]


class ToastImageAndText2(Toast):
    """
    An image, one string of bold text on the first line, one string of regular text
    wrapped across the second and third lines
    """

    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_IMAGE_AND_TEXT02]] = ToastTemplateType.TOAST_IMAGE_AND_TEXT02
    HasImage: ClassVar[Literal[True]] = True

    def __init__(self) -> None:
        super().__init__()
        self.textFields = ["", ""]


# noinspection DuplicatedCode
class ToastImageAndText3(Toast):
    """
    An image, one string of bold text on the first line, one string of regular
    text wrapped across the second and third lines
    """

    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_IMAGE_AND_TEXT03]] = ToastTemplateType.TOAST_IMAGE_AND_TEXT03
    HasImage: ClassVar[Literal[True]] = True

    def __init__(self) -> None:
        super().__init__()
        self.textFields = ["", ""]


class ToastImageAndText4(Toast):
    """
    An image, one string of bold text on the first line, one string of regular text
    on the second line, one string of regular text on the third line
    """

    ToastType: ClassVar[Literal[ToastTemplateType.TOAST_IMAGE_AND_TEXT04]] = ToastTemplateType.TOAST_IMAGE_AND_TEXT04
    HasImage: ClassVar[Literal[True]] = True

    def __init__(self) -> None:
        super().__init__()
        self.textFields = ["", "", ""]
