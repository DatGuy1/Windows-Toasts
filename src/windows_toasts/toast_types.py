from __future__ import annotations

import warnings
from enum import Enum
from pathlib import Path
from typing import Callable

from winsdk.windows.ui.notifications import (
    ToastActivatedEventArgs,
    ToastDismissedEventArgs,
    ToastFailedEventArgs,
    ToastTemplateType
)

from .toast_audio import ToastAudio


class ToastDuration(Enum):
    Default = "Default"
    Short = "short"
    Long = "long"


class Toast:
    ToastType = None

    def __init__(self):
        """
        Base class for a toast. Should not be directly created
        """
        self.audio: ToastAudio = ToastAudio()
        self.duration: ToastDuration = ToastDuration.Default
        self.hasImage: bool = False
        self.imagePath: Path | None = None
        self.textFields: list = []

        self.on_activated: Callable[[ToastActivatedEventArgs], None] | None = None
        self.on_dismissed: Callable[[ToastDismissedEventArgs], None] | None = None
        self.on_failed: Callable[[ToastFailedEventArgs], None] | None = None

    def SetHeadline(self, headlineText: str) -> None:
        """
        Sets the headline (top line) for the toast. Use SetBody if toast has only one line
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

    def SetImage(self, imagePath: str | Path):
        """
        Sets the image that will be displayed as the icon of the toast. Only works for ToastImageAndText classes

        :param imagePath: The absolute or relative path to an image file
        :type imagePath: str
        """
        if isinstance(imagePath, str):
            imagePath = Path(imagePath)

        self.imagePath = imagePath.resolve()


class ToastText1(Toast):
    ToastType = ToastTemplateType.TOAST_TEXT01

    def __init__(self):
        """
        A single string wrapped across a maximum of three lines of text
        """
        super().__init__()
        self.textFields = [""]


class ToastText2(Toast):
    ToastType = ToastTemplateType.TOAST_TEXT02

    def __init__(self):
        """
        One string of bold text on the first line, one string of regular text wrapped across the second and third lines
        """
        super().__init__()
        self.textFields = [""]


class ToastText3(Toast):
    ToastType = ToastTemplateType.TOAST_TEXT03

    def __init__(self):
        """
        One string of bold text wrapped across the first and second lines, one string of regular text on the third line
        """
        super().__init__()
        self.textFields = ["", "", ""]


class ToastText4(Toast):
    ToastType = ToastTemplateType.TOAST_TEXT04

    def __init__(self):
        """
        One string of bold text on the first line, one string of regular text on the second line,
        one string of regular text on the third line
        """
        super().__init__()
        self.textFields = ["", "", ""]


class ToastImageAndText1(Toast):
    ToastType = ToastTemplateType.TOAST_IMAGE_AND_TEXT01

    def __init__(self):
        """
        An image and a single string wrapped across a maximum of three lines of text
        """
        super().__init__()
        self.textFields = [""]
        self.hasImage = True


class ToastImageAndText2(Toast):
    ToastType = ToastTemplateType.TOAST_IMAGE_AND_TEXT02

    def __init__(self):
        """
        An image, one string of bold text on the first line, one string of regular text
        wrapped across the second and third lines
        """
        super().__init__()
        self.textFields = ["", ""]
        self.hasImage = True


class ToastImageAndText3(Toast):
    ToastType = ToastTemplateType.TOAST_IMAGE_AND_TEXT03

    def __init__(self):
        """
        An image, one string of bold text on the first line, one string of regular
        text wrapped across the second and third lines
        """
        super().__init__()
        self.textFields = ["", ""]
        self.hasImage = True


class ToastImageAndText4(Toast):
    ToastType = ToastTemplateType.TOAST_IMAGE_AND_TEXT04

    def __init__(self):
        """
        An image, one string of bold text on the first line, one string of regular text
        on the second line, one string of regular text on the third line
        """
        super().__init__()
        self.textFields = ["", "", ""]
        self.hasImage = True
