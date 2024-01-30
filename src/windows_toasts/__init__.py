import platform

from .exceptions import UnsupportedOSVersionException

# We'll assume it's Windows since if it's on another OS it should be self-explanatory
MIN_VERSION = 10240
if platform.system() == "Windows" and (osVersion := int(platform.version().split(".")[2])) < MIN_VERSION:
    raise UnsupportedOSVersionException(
        f"Platform version {osVersion} is not supported. Required minimum is {MIN_VERSION}"
    )

from ._version import __author__, __description__, __license__, __title__, __url__, __version__  # noqa: F401
from .events import ToastActivatedEventArgs, ToastDismissalReason, ToastDismissedEventArgs, ToastFailedEventArgs
from .exceptions import InvalidImageException, ToastNotFoundError
from .toast import Toast
from .toast_audio import AudioSource, ToastAudio
from .toasters import InteractableWindowsToaster, WindowsToaster
from .wrappers import (
    ToastButton,
    ToastButtonColour,
    ToastDisplayImage,
    ToastDuration,
    ToastImage,
    ToastImagePosition,
    ToastInputSelectionBox,
    ToastInputTextBox,
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
    "Toast",
    # toasters.py
    "InteractableWindowsToaster",
    "WindowsToaster",
    # wrappers.py
    "ToastButton",
    "ToastButtonColour",
    "ToastDisplayImage",
    "ToastDuration",
    "ToastImage",
    "ToastImagePosition",
    "ToastInputSelectionBox",
    "ToastInputTextBox",
    "ToastProgressBar",
    "ToastScenario",
    "ToastSelection",
    "ToastSystemButton",
    "ToastSystemButtonAction",
]
