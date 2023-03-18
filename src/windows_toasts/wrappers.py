from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Optional, Sequence, Union
from urllib.parse import urlparse


class ToastDuration(Enum):
    """
    Possible values for duration to display toast for
    """

    Default: str = "Default"
    Short: str = "short"
    Long: str = "long"


class ToastScenario(Enum):
    """
    Possible scenarios for the toast
    """

    Default: str = ""
    """The default; nothing special"""
    Alarm: str = "alarm"
    """Causes the toast to stay on-screen and expanded until the user takes action as well as a default looping sound"""
    Reminder: str = "reminder"
    """The toast will stay on-screen and expanded until the user takes action"""
    IncomingCall: str = "incomingCall"
    """
    The Toast will stay on-screen and expanded until the user takes action (on Mobile this expands to full screen). \
    Also causes a looping incoming call sound to be selected by default.
    """
    Important: str = "urgent"
    """
    Important notifications allow users to have more control over what 1st party and 3rd party apps can send them \
    high-priority app notifications that can break through Focus Assist (Do not Disturb). \
    This can be modified in the notifications settings.
    """


class ToastButtonColour(Enum):
    """
    Possible colours for toast buttons
    """

    Default = ""
    Green = "Success"
    Red = "Critical"


@dataclass(init=False)
class ToastImage:
    """
    Image that can be displayed in various toast elements
    """

    path: str
    """The URI of the image source"""

    def __init__(self, imagePath: Union[str, PathLike]):
        """
        Initialise an :class:`ToastImage` class to use in certain classes
        Online images are supported only in packaged apps that have the internet capability in their manifest.
        Unpackaged apps don't support http images; you must download the image to your local app data,
        and reference it locally.

        :param imagePath: The path to an image file
        :type imagePath: Union[str, PathLike]
        :raises: ValueError: If the path to an online image is supplied
        """
        if isinstance(imagePath, str) and urlparse(imagePath).scheme in ("http", "https"):
            raise ValueError("Online images are not supported")
        elif not isinstance(imagePath, Path):
            imagePath = Path(imagePath)

        self.path = imagePath.as_uri()


@dataclass
class ToastDisplayImage:
    """
    Define an image that will be displayed as the icon of the toast
    """

    image: ToastImage
    """An image file"""
    altText: Optional[str] = None
    """A description of the image, for users of assistive technologies"""
    large: bool = False
    """
    Whether to set the image as large and at the top/bottom, or small and to the left. \
    Only works on :class:`InteractableWindowsToaster`
    """
    circleCrop: bool = True
    """
    If the image is not marked as large, whether to crop the image as a circle, or leave it as a square
    """

    @classmethod
    def fromPath(
        cls,
        imagePath: Union[str, PathLike],
        altText: Optional[str] = None,
        large: bool = False,
        circleCrop: bool = True,
    ) -> ToastDisplayImage:
        """
        Create a :class:`ToastDisplayImage` object from path without having to create :class:`ToastImage`
        """
        image = ToastImage(imagePath)
        return cls(image, altText, large, circleCrop)


@dataclass
class ToastProgressBar:
    """
    Progress bar to be included in a toast
    """

    status: str
    """
    Status string, which is displayed underneath the progress bar on the left. \
    This string should reflect the status of the operation, like "Downloading..." or "Installing..."
    """
    caption: Optional[str] = None
    """An optional title string"""
    progress: Optional[float] = 0
    """
    The percentage value of the progress bar, {0..1}. Defaults to zero.
    If set to None, it will use an indeterminate bar
    """
    progress_override: Optional[str] = None
    """Optional string to be displayed instead of the default percentage string"""


@dataclass
class _ToastInput(abc.ABC):
    """
    Base input dataclass to be used in toasts
    """

    input_id: str
    """Identifier to use for the input"""
    caption: str = ""
    """Optional caption to display near the input"""


@dataclass(init=False)
class ToastInputTextBox(_ToastInput):
    """
    A text box that can be added in toasts for the user to enter their input
    """

    placeholder: str = ""
    """Optional placeholder for a text input box"""

    def __init__(self, input_id: str, caption: str = "", placeholder: str = ""):
        super().__init__(input_id, caption)
        self.placeholder = placeholder


@dataclass
class ToastSelection:
    """
    An item that the user can select from the drop down list
    """

    selection_id: str
    """Identifier for the selection"""
    content: str
    """Value for the selection to display"""


@dataclass(init=False)
class ToastInputSelectionBox(_ToastInput):
    """
    A selection box control, which lets users pick from a dropdown list of options
    """

    selections: Sequence[ToastSelection] = ()
    """Sequence of selections to include in the box"""
    default_selection: Optional[ToastSelection] = None
    """Selection to default to. If None, the default selection will be empty"""

    def __init__(
        self,
        input_id: str,
        caption: str = "",
        selections: Sequence[ToastSelection] = (),
        default_selection: Optional[ToastSelection] = None,
    ):
        super().__init__(input_id, caption)
        self.selections = selections
        self.default_selection = default_selection


@dataclass
class ToastButton:
    """
    A button that the user can click on a toast notification
    """

    content: str = ""
    """The content displayed on the button"""
    arguments: str = ""
    """String of arguments that the app will later receive if the user clicks this button"""
    image: Optional[ToastImage] = None
    """An image to be used as an icon for the button"""
    relatedInput: Optional[Union[ToastInputTextBox, ToastInputSelectionBox]] = None
    """An input to position the button besides"""
    inContextMenu: bool = False
    """Whether to place the button in the context menu rather than the actual toast"""
    tooltip: Optional[str] = None
    """The tooltip for a button, if the button has an empty content string"""
    colour: ToastButtonColour = ToastButtonColour.Default
    """:class:`ToastButtonColour` for the button"""
