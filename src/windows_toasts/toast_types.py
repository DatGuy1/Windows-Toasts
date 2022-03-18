import warnings
from enum import Enum
from pathlib import Path

from winsdk.windows.ui.notifications import ToastTemplateType


class ToastDuration(Enum):
    Default = "Default"
    Short = "short"
    Long = "long"


class Toast:
    ToastType = None
    HasImage = False

    def __init__(self):
        """
        Base class for a toast. Should not be directly created
        """
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

    def AddAction(self, actionName, actionArguments):
        """
        Add an action to the action list. For example, if you're setting up a reminder,
        you would use 'action=remindlater&date=2020-01-20' as arguments. Maximum of five.

        :param actionName: Value that will be displayed on the button
        :type actionName: str
        :param actionArguments: Arguments that will be available in the callback.
        :type actionArguments: str
        """
        if len(self.actions) >= 5:
            warnings.warn("Cannot add any more actions, you're already at five")
            return

        self.actions.append((actionName, actionArguments))

    def SetHeadline(self, headlineText):
        """
        Sets the headline (top line) for the toast. Warns to use SetBody if toast has only one line
        """
        if len(self.textFields) < 2:
            warnings.warn(f"Toast of type {self.__class__.__name__} has no headline, only a body")

        self.textFields[0] = headlineText

    def SetBody(self, bodyText):
        """
        Sets the text that will be displayed in the body of a single-lined toast
        """
        if len(self.textFields) == 1:
            self.textFields[0] = bodyText
        else:
            self.SetFirstLine(bodyText)

    def SetFirstLine(self, lineText):
        """
        Sets the text that will be displayed in the first line (not the headline) of a multi-lined toast
        """
        self.textFields[1] = lineText

    def SetSecondLine(self, lineText):
        """
        Sets the text that will be displayed in the second line of a two-lined (plus headline) toast
        """
        self.textFields[2] = lineText

    def SetImage(self, imagePath):
        """
        Sets the image that will be displayed as the icon of the toast. Only works for ToastImageAndText classes

        :param imagePath: The absolute or relative path to an image file
        :type imagePath: str
        """
        if isinstance(imagePath, str):
            imagePath = Path(imagePath)

        self.imagePath = imagePath.resolve()

    def SetInputField(self, placeholderText):
        """
        Adds an input field to the notification. It will be supplied as user_input of type ValueSet in on_activated
        :param placeholderText: Placeholder text to display the the input field
        :type placeholderText: str
        """
        self.textInputPlaceholder = placeholderText

    def SetCustomTimestamp(self, notificationTime):
        """
        Sets a custom notification timestamp. If you don't provide a custom timestamp,
        Windows uses the time that your notification was sent
        """
        self.timestamp = notificationTime


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
        self.textFields = ["", ""]


class ToastText3(Toast):
    ToastType = ToastTemplateType.TOAST_TEXT03

    def __init__(self):
        """
        One string of bold text wrapped across the first and second lines, one string of regular text on the third line
        """
        super().__init__()
        self.textFields = ["", ""]


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
    HasImage = True

    def __init__(self):
        """
        An image and a single string wrapped across a maximum of three lines of text
        """
        super().__init__()
        self.textFields = [""]


class ToastImageAndText2(Toast):
    ToastType = ToastTemplateType.TOAST_IMAGE_AND_TEXT02
    HasImage = True

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
    HasImage = True

    def __init__(self):
        """
        An image, one string of bold text on the first line, one string of regular
        text wrapped across the second and third lines
        """
        super().__init__()
        self.textFields = ["", ""]


class ToastImageAndText4(Toast):
    ToastType = ToastTemplateType.TOAST_IMAGE_AND_TEXT04
    HasImage = True

    def __init__(self):
        """
        An image, one string of bold text on the first line, one string of regular text
        on the second line, one string of regular text on the third line
        """
        super().__init__()
        self.textFields = ["", "", ""]
