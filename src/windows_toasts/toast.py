from __future__ import annotations

import copy
import datetime
import urllib.parse
import uuid
import warnings
from collections.abc import Iterable
from typing import Callable, Optional, Union

from winrt.windows.ui.notifications import ToastDismissedEventArgs, ToastFailedEventArgs

from .events import ToastActivatedEventArgs
from .toast_audio import ToastAudio
from .wrappers import (
    ToastButton,
    ToastDisplayImage,
    ToastDuration,
    ToastInputSelectionBox,
    ToastInputTextBox,
    ToastProgressBar,
    ToastScenario,
    ToastSystemButton,
)

ToastInput = Union[ToastInputTextBox, ToastInputSelectionBox]


class Toast:
    audio: Optional[ToastAudio]
    """The custom audio configuration for the toast"""
    duration: ToastDuration
    """:class:`~windows_toasts.wrappers.ToastDuration`, be it the default, short, or long"""
    expiration_time: Optional[datetime.datetime]
    """The time for the toast to expire on in the action center. If it is on-screen, nothing will happen"""
    group: Optional[str]
    """An internal identifier, where you can assign groups like "wallPosts", "messages", "friendRequests", etc."""
    scenario: ToastScenario
    """Scenario for the toast"""
    suppress_popup: bool
    """Whether to suppress the toast popup and relegate it immediately to the action center"""
    timestamp: Optional[datetime.datetime]
    """A custom timestamp. If you don't provide one, Windows uses the time that your notification was sent"""
    progress_bar: Optional[ToastProgressBar]
    """An adjustable progress bar for the toast"""
    attribution_text: Optional[str]
    """Text displayed below any text elements, but above inline images"""
    on_activated: Optional[Callable[[ToastActivatedEventArgs], None]]
    """Callable to execute when the toast is clicked if basic, or a button is clicked if interactable"""
    on_dismissed: Optional[Callable[[ToastDismissedEventArgs], None]]
    """Callable to execute when the toast is dismissed (X is clicked or times out) if interactable"""
    on_failed: Optional[Callable[[ToastFailedEventArgs], None]]
    """Callable to execute when the toast fails to display"""
    actions: list[Union[ToastButton, ToastSystemButton]]
    """List of buttons to include. Implemented through :func:`AddAction`"""
    images: list[ToastDisplayImage]
    """See :func:`AddImage`"""
    inputs: list[ToastInput]
    """Text/selection input boxes"""
    text_fields: list[Optional[str]]
    """Various text fields"""
    tag: str
    """Unique tag for the toast, automatically set as a UUID"""
    updates: int
    """Number of times the toast has been updated; mostly for internal use"""
    _launch_action: Optional[str]
    """Protocol to launch when the toast is clicked"""

    def __init__(
        self,
        text_fields: Union[None, list[Optional[str]], tuple[Optional[str]], set[Optional[str]]] = None,
        audio: Optional[ToastAudio] = None,
        duration: ToastDuration = ToastDuration.Default,
        expiration_time: Optional[datetime.datetime] = None,
        group: Optional[str] = None,
        launch_action: Optional[str] = None,
        progress_bar: Optional[ToastProgressBar] = None,
        attribution_text: Optional[str] = None,
        scenario: ToastScenario = ToastScenario.Default,
        suppress_popup: bool = False,
        timestamp: Optional[datetime.datetime] = None,
        on_activated: Optional[Callable[[ToastActivatedEventArgs], None]] = None,
        on_dismissed: Optional[Callable[[ToastDismissedEventArgs], None]] = None,
        on_failed: Optional[Callable[[ToastFailedEventArgs], None]] = None,
        actions: Iterable[Union[ToastButton, ToastSystemButton]] = (),
        images: Iterable[ToastDisplayImage] = (),
        inputs: Iterable[ToastInput] = (),
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
        self.audio = audio
        self.duration = duration
        self.scenario = scenario
        self.progress_bar = progress_bar
        self.attribution_text = attribution_text
        self.timestamp = timestamp
        self.group = group
        self.expiration_time = expiration_time
        self.suppress_popup = suppress_popup
        self.launch_action = launch_action

        self.actions = []
        self.images = []
        self.inputs = []
        self.text_fields = [] if text_fields is None else list(text_fields)

        for action in actions:
            self.AddAction(action)

        for image in images:
            self.AddImage(image)

        for toast_input in inputs:
            self.AddInput(toast_input)

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

    def AddAction(self, action: Union[ToastButton, ToastSystemButton]) -> None:
        """
        Add an action to the action list. For example, if you're setting up a reminder,
        you would use 'action=remindlater&date=2020-01-20' as arguments. Maximum of five.

        :type action: Union[ToastButton, ToastSystemButton]
        """
        if len(self.actions) + len(self.inputs) >= 5:
            warnings.warn(
                f"Cannot add action '{action.content}', you've already reached the maximum of five actions + inputs"
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
                f"you've already reached the maximum of five actions + inputs"
            )
            return

        self.inputs.append(toast_input)

    @property
    def launch_action(self) -> Optional[str]:
        """Protocol to launch when the toast is clicked"""
        return self._launch_action

    @launch_action.setter
    def launch_action(self, value: Optional[str]):
        if value is None:
            self._launch_action = None
        else:
            if not urllib.parse.urlparse(value).scheme:
                warnings.warn(f"Ensure your launch action of {value} is of a proper protocol")

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
