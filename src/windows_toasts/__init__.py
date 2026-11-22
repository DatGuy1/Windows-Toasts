import platform

from .exceptions import UnsupportedOSVersionException

# We'll assume it's Windows since if it's on another OS it should be self-explanatory
MIN_VERSION = 10240
if platform.system() == "Windows" and (osVersion := int(platform.version().split(".")[2])) < MIN_VERSION:
    raise UnsupportedOSVersionException(
        f"Platform version {osVersion} is not supported. Required minimum is {MIN_VERSION}"
    )

from ._version import __author__, __description__, __license__, __title__, __url__, __version__
from .activation import launched_by_toast
from .adaptive import (
    ToastGroup,
    ToastGroupImage,
    ToastImageAlign,
    ToastSubgroup,
    ToastText,
    ToastTextAlign,
    ToastTextStacking,
    ToastTextStyle,
)
from .events import ToastActivatedEventArgs, ToastDismissalReason, ToastDismissedEventArgs, ToastFailedEventArgs
from .exceptions import InvalidImageException, ToastNotFoundError
from .toast import ActionCenterToast, Toast
from .toast_audio import AudioSource, ToastAudio
from .toasters import InteractableWindowsToaster, WindowsToaster
from .wrappers import (
    NotificationSetting,
    ToastButton,
    ToastButtonColour,
    ToastDisplayImage,
    ToastDuration,
    ToastHeader,
    ToastImage,
    ToastImagePosition,
    ToastInputSelectionBox,
    ToastInputTextBox,
    ToastNotificationMode,
    ToastProgressBar,
    ToastScenario,
    ToastSelection,
    ToastSystemButton,
    ToastSystemButtonAction,
)

__all__ = [
    # _version.py
    "__author__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    # activation.py
    "launched_by_toast",
    # adaptive.py
    "ToastGroup",
    "ToastGroupImage",
    "ToastImageAlign",
    "ToastSubgroup",
    "ToastText",
    "ToastTextAlign",
    "ToastTextStacking",
    "ToastTextStyle",
    # events.py
    "ToastActivatedEventArgs",
    "ToastDismissalReason",
    "ToastDismissedEventArgs",
    "ToastFailedEventArgs",
    # exceptions.py
    "InvalidImageException",
    "ToastNotFoundError",
    "UnsupportedOSVersionException",
    # toast_audio.py
    "AudioSource",
    "ToastAudio",
    # toast.py
    "ActionCenterToast",
    "Toast",
    # toasters.py
    "InteractableWindowsToaster",
    "WindowsToaster",
    # wrappers.py
    "NotificationSetting",
    "ToastButton",
    "ToastButtonColour",
    "ToastDisplayImage",
    "ToastDuration",
    "ToastHeader",
    "ToastImage",
    "ToastImagePosition",
    "ToastInputSelectionBox",
    "ToastInputTextBox",
    "ToastNotificationMode",
    "ToastProgressBar",
    "ToastScenario",
    "ToastSelection",
    "ToastSystemButton",
    "ToastSystemButtonAction",
]
