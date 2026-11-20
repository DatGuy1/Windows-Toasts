from __future__ import annotations

import copy
import datetime
import functools
import urllib.parse
import uuid
import warnings
from collections.abc import Callable, Iterable
from typing import Any, TypeVar, cast

from .events import ToastActivatedEventArgs, ToastDismissedEventArgs, ToastFailedEventArgs
from .toast_audio import ToastAudio
from .wrappers import (
    ToastButton,
    ToastDisplayImage,
    ToastDuration,
    ToastHeader,
    ToastInputSelectionBox,
    ToastInputTextBox,
    ToastProgressBar,
    ToastScenario,
    ToastSystemButton,
)

ToastInput = ToastInputTextBox | ToastInputSelectionBox

InitT = TypeVar("InitT", bound=Callable[..., None])

# The order Toast.__init__ used to accept these positionally in, after text_fields
_LEGACY_POSITIONAL_PARAMETERS = (
    "audio",
    "duration",
    "expiration_time",
    "group",
    "launch_action",
    "progress_bar",
    "attribution_text",
    "scenario",
    "suppress_popup",
    "timestamp",
    "on_activated",
    "on_dismissed",
    "on_failed",
    "actions",
    "images",
    "inputs",
)


def _deprecate_positional_parameters(init: InitT) -> InitT:
    """
    Keep accepting the arguments that followed text_fields positionally, in their old order, with a warning
    """

    @functools.wraps(init)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        # args[0] is self and args[1] is text_fields
        legacyArgs = args[2:]
        if legacyArgs:
            if len(legacyArgs) > len(_LEGACY_POSITIONAL_PARAMETERS):
                raise TypeError(
                    f"Toast() takes at most {len(_LEGACY_POSITIONAL_PARAMETERS) + 1} positional arguments "
                    f"but {len(args) - 1} were given"
                )

            legacyNames = _LEGACY_POSITIONAL_PARAMETERS[: len(legacyArgs)]
            for name in legacyNames:
                if name in kwargs:
                    raise TypeError(f"Toast() got multiple values for argument '{name}'")

            warnings.warn(
                "Passing Toast arguments other than text_fields positionally is deprecated. "
                f"Pass {', '.join(legacyNames)} as keyword arguments instead",
                DeprecationWarning,
                stacklevel=2,
            )
            kwargs.update(zip(legacyNames, legacyArgs, strict=True))

        init(*args[:2], **kwargs)

    # noinspection PyUnnecessaryCast
    return cast(InitT, wrapper)


class Toast:
    text_fields: list[str | None]
    """Various text fields"""
    images: list[ToastDisplayImage]
    """See :func:`AddImage`"""
    inputs: list[ToastInput]
    """Text/selection input boxes"""
    actions: list[ToastButton | ToastSystemButton]
    """List of buttons to include. Implemented through :func:`AddAction`"""
    progress_bar: ToastProgressBar | None
    """An adjustable progress bar for the toast"""
    attribution_text: str | None
    """Text displayed below any text elements, but above inline images"""
    audio: ToastAudio | None
    """The custom audio configuration for the toast"""
    duration: ToastDuration
    """:class:`~windows_toasts.wrappers.ToastDuration`, be it the default, short, or long"""
    scenario: ToastScenario
    """Scenario for the toast"""
    suppress_popup: bool
    """Whether to suppress the toast popup and relegate it immediately to the action center"""
    timestamp: datetime.datetime | None
    """A custom timestamp. If you don't provide one, Windows uses the time that your notification was sent"""
    group: str | None
    """An internal identifier, where you can assign groups like "wallPosts", "messages", "friendRequests", etc."""
    header: ToastHeader | None
    """A header to show the toast under in Action Center. Unlike group, this is visible to the user"""
    expiration_time: datetime.datetime | None
    """The time for the toast to expire on in the action center. If it is on-screen, nothing will happen"""
    expires_on_reboot: bool
    """Whether to remove the toast from the action center when the device restarts. Ignored for scheduled toasts"""
    on_activated: Callable[[ToastActivatedEventArgs], None] | None
    """Callable to execute when the toast is clicked if basic, or a button is clicked if interactable"""
    on_dismissed: Callable[[ToastDismissedEventArgs], None] | None
    """Callable to execute when the toast is dismissed (X is clicked or times out) if interactable"""
    on_failed: Callable[[ToastFailedEventArgs], None] | None
    """Callable to execute when the toast fails to display"""
    tag: str
    """Unique tag for the toast, automatically set as a UUID"""
    updates: int
    """Number of times the toast has been updated; mostly for internal use"""
    _launch_action: str | None
    """Protocol to launch when the toast is clicked"""

    @_deprecate_positional_parameters
    def __init__(
        self,
        text_fields: list[str | None] | tuple[str | None] | set[str | None] | None = None,
        *,
        images: Iterable[ToastDisplayImage] = (),
        inputs: Iterable[ToastInput] = (),
        actions: Iterable[ToastButton | ToastSystemButton] = (),
        progress_bar: ToastProgressBar | None = None,
        attribution_text: str | None = None,
        audio: ToastAudio | None = None,
        duration: ToastDuration = ToastDuration.Default,
        scenario: ToastScenario = ToastScenario.Default,
        suppress_popup: bool = False,
        timestamp: datetime.datetime | None = None,
        group: str | None = None,
        header: ToastHeader | None = None,
        expiration_time: datetime.datetime | None = None,
        expires_on_reboot: bool = False,
        launch_action: str | None = None,
        on_activated: Callable[[ToastActivatedEventArgs], None] | None = None,
        on_dismissed: Callable[[ToastDismissedEventArgs], None] | None = None,
        on_failed: Callable[[ToastFailedEventArgs], None] | None = None,
    ) -> None:
        """
        Initialise a toast

        :param actions: Iterable of actions to add; see :meth:`AddAction`
        :type actions: Iterable[Union[ToastButton, ToastSystemButton]]
        :param images: See :meth:`AddImage`
        :type images: Iterable[ToastDisplayImage]
        :param inputs: See :meth:`AddInput`
        :type inputs: Iterable[ToastInput]
        """
        self.text_fields = [] if text_fields is None else list(text_fields)
        self.images = []
        self.inputs = []
        self.actions = []

        for image in images:
            self.AddImage(image)

        # Actions go first so that past the limit of five actions + inputs it's the inputs that get dropped
        for action in actions:
            self.AddAction(action)

        for toast_input in inputs:
            self.AddInput(toast_input)

        self.progress_bar = progress_bar
        self.attribution_text = attribution_text
        self.audio = audio
        self.duration = duration
        self.scenario = scenario
        self.suppress_popup = suppress_popup
        self.timestamp = timestamp
        self.group = group
        self.header = header
        self.expiration_time = expiration_time
        self.expires_on_reboot = expires_on_reboot
        self.launch_action = launch_action
        self.on_activated = on_activated
        self.on_dismissed = on_dismissed
        self.on_failed = on_failed

        self.tag = str(uuid.uuid4())
        self.updates = 0

    def __eq__(self, other):
        if isinstance(other, Toast):
            return other.tag == self.tag

        return False

    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))

    def AddAction(self, action: ToastButton | ToastSystemButton) -> None:
        """
        Add an action to the action list. For example, if you're setting up a reminder,
        you would use 'action=remindlater&date=2020-01-20' as arguments. Maximum of five.

        :type action: Union[ToastButton, ToastSystemButton]
        """
        if len(self.actions) + len(self.inputs) >= 5:
            warnings.warn(
                f"Cannot add action '{action.content}', you've already reached the maximum of five actions + inputs",
                stacklevel=2,
            )
            return

        self.actions.append(action)

    def AddImage(self, image: ToastDisplayImage) -> None:
        """
        Adds an the image that will be displayed on the toast.
        If using WindowsToaster, a maximum of two (one as the logo and one hero) images will work.

        :param image: :class:`ToastDisplayImage` to display in the toast
        """
        self.images.append(image)

    def AddInput(self, toast_input: ToastInput) -> None:
        """
        Adds an input field to the notification. It will be supplied as user_input of type ValueSet in on_activated

        :param toast_input: :class:`ToastInput` to display in the toast
        """
        if len(self.actions) + len(self.inputs) >= 5:
            warnings.warn(
                f"Cannot add input '{toast_input.input_id}', "
                f"you've already reached the maximum of five actions + inputs",
                stacklevel=2,
            )
            return

        self.inputs.append(toast_input)

    @property
    def launch_action(self) -> str | None:
        """Protocol to launch when the toast is clicked"""
        return self._launch_action

    @launch_action.setter
    def launch_action(self, value: str | None):
        if value is None:
            self._launch_action = None
        else:
            if not urllib.parse.urlparse(value).scheme:
                warnings.warn(f"Ensure your launch action of {value} is of a proper protocol", stacklevel=2)

            self._launch_action = value

    def clone(self) -> Toast:
        """
        Clone the current toast and return the new one

        :return: A deep copy of the toast
        :rtype: Toast
        """
        newToast = copy.deepcopy(self)
        newToast.tag = str(uuid.uuid4())

        return newToast
