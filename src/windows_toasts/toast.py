from __future__ import annotations

import copy
import datetime
import urllib.parse
import uuid
import warnings
from typing import Callable, Iterable, List, Literal, Optional, TypeVar

from toasts_winrt.windows.ui.notifications import ToastDismissedEventArgs, ToastFailedEventArgs

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
)

ToastInput = TypeVar("ToastInput", ToastInputTextBox, ToastInputSelectionBox)


class Toast:
    """
    Base class for a toast. Should not be directly created or used as there are specific SetX() methods for it
    """

    audio: Optional[ToastAudio]
    """Audio configuration"""
    actions: List[ToastButton]
    """List of buttons to include. Implemented through :func:`AddAction`"""
    duration: Literal[ToastDuration.Default, ToastDuration.Long, ToastDuration.Short]
    """:class:`~windows_toasts.wrappers.ToastDuration` enum, be it the default, short, or long"""
    images: List[ToastDisplayImage]
    """See :func:`AddImage`"""
    scenario: ToastScenario
    """Scenario for the toast"""
    textFields: List[Optional[str]]
    """Various text fields (dependant on subclass)"""
    inputs: List[ToastInput]
    """Placeholder for a text input box"""
    timestamp: Optional[datetime.datetime]
    """See :func:`SetCustomTimestamp`"""
    progress_bar: Optional[ToastProgressBar] = None
    """See :func:`SetProgressBar`"""
    group: Optional[str] = None
    """Group to place the toast in"""
    tag: str
    """uuid of a tag for the toast"""
    updates: int
    """Number of times the toast has been updated"""
    expiration_time: Optional[datetime.datetime] = None
    """Expiration time of the toast"""
    suppress_popup: bool = False
    """Whether to suppress the toast popup and relegate it immediately to the action center"""
    launch_action: Optional[str] = None
    """Protocol to launch when the toast is clicked"""
    on_activated: Optional[Callable[[ToastActivatedEventArgs], None]]
    """Callable to execute when the toast is clicked if basic, or a button is clicked if interactable"""
    on_dismissed: Optional[Callable[[ToastDismissedEventArgs], None]]
    """Callable to execute when the toast is dismissed (X is clicked or times out) if interactable"""
    on_failed: Optional[Callable[[ToastFailedEventArgs], None]]
    """Callable to execute when the toast fails to display"""

    def __init__(
        self,
        first_line: Optional[str] = None,
        audio: Optional[ToastAudio] = None,
        actions: Iterable[ToastButton] = (),
        duration: ToastDuration = ToastDuration.Default,
        scenario: ToastScenario = ToastScenario.Default,
        progress_bar: Optional[ToastProgressBar] = None,
        second_line: Optional[str] = None,
        third_line: Optional[str] = None,
        images: Iterable[ToastDisplayImage] = (),
        inputs: Iterable[ToastInput] = (),
        timestamp: Optional[datetime.datetime] = None,
        group: Optional[str] = None,
        expiration_time: Optional[datetime.datetime] = None,
        suppress_popup: bool = False,
        launch_action: Optional[str] = None,
        on_activated: Optional[Callable[[ToastActivatedEventArgs], None]] = None,
        on_dismissed: Optional[Callable[[ToastDismissedEventArgs], None]] = None,
        on_failed: Optional[Callable[[ToastFailedEventArgs], None]] = None,
    ) -> None:
        """
        Initialise a toast

        :param audio: See :meth:`SetAudio`
        :type audio: Optional[ToastAudio]
        :param actions: Iterable of actions to add; see :meth:`AddAction`
        :type actions: Iterable[ToastButton]
        :param duration: See :meth:`SetDuration`
        :type duration: ToastDuration
        :param scenario: See :meth:`SetScenario`
        :type scenario: ToastScenario
        :param progress_bar: See :meth:`SetProgressBar`
        :type progress_bar: Optional[ToastProgressBar]
        :param first_line: See :meth:`SetFirstLine`
        :type first_line: Optional[str]
        :param second_line: See :meth:`SetSecondLine`
        :type second_line: Optional[str]
        :param third_line: See :meth:`SetThirdLine`
        :type third_line: Optional[str]
        :param images: See :meth:`AddImage`
        :type images: Iterable[ToastDisplayImage]
        :param inputs: See :meth:`AddInput`
        :type inputs: Iterable[ToastInput]
        :param timestamp: See :meth:`SetCustomTimestamp`
        :type timestamp: Optional[datetime.datetime]
        :param group: See :meth:`SetGroup`
        :type group: Optional[str]
        :param expiration_time: See :meth:`SetExpirationTime`
        :type expiration_time: Optional[datetime.datetime]
        :param suppress_popup: See :meth:`SetSuppressPopup`
        :type suppress_popup: bool
        :param launch_action: See :meth:`SetLaunchAction`
        :type launch_action: Optional[str]
        :param on_activated: Callable to execute when the toast is clicked if basic, or a button is clicked if \
         interactable
        :type on_activated: Optional[Callable[[ToastActivatedEventArgs], None]]
        :param on_dismissed: Callable to execute when the toast is dismissed (X is clicked or times out) if interactable
        :type on_dismissed: Optional[Callable[[ToastDismissedEventArgs], None]]
        :param on_failed: Callable to execute when the toast fails to display
        :type on_failed:  Optional[Callable[[ToastFailedEventArgs], None]]
        """
        self.actions = []
        self.inputs = []
        self.images = []
        # Maximum of three text fields (at least until groups are implemented)
        self.textFields = [None, None, None]

        self.SetAudio(audio)
        self.SetDuration(duration)
        self.SetScenario(scenario)
        self.SetCustomTimestamp(timestamp)
        self.SetGroup(group)
        self.SetProgressBar(progress_bar)
        self.SetExpirationTime(expiration_time)
        self.SetSuppressPopup(suppress_popup)
        self.SetLaunchAction(launch_action)

        # Certainly not the best way to do this now we've moved away from templates. Maybe expose textFields further?
        # The behaviour of only exposing Add[Image/Input] without having an easy way to remove it is poor convention
        # that I want to remove ASAP
        if first_line is not None:
            self.SetFirstLine(first_line)
        if second_line is not None:
            self.SetSecondLine(second_line)
        if third_line is not None:
            self.SetThirdLine(third_line)

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

    def SetAudio(self, audio: Optional[ToastAudio]) -> None:
        """
        Sets the custom audio configuration for the toast
        """
        self.audio = audio

    def SetDuration(self, duration: ToastDuration) -> None:
        """
        Set the display duration for the toast
        """
        self.duration = duration

    def SetScenario(self, scenario: ToastScenario) -> None:
        """
        Set whether Windows should consider the notification as important
        """
        self.scenario = scenario

    def SetProgressBar(self, progressBar: Optional[ToastProgressBar]) -> None:
        """
        Set a adjustable progress bar for the toast
        """
        self.progress_bar = progressBar

    def SetGroup(self, group: Optional[str]) -> None:
        """
        Set a group for the toast. Group is a generic identifier, where you can assign groups like \
        "wallPosts", "messages", "friendRequests", etc.
        """
        self.group = group

    def SetFirstLine(self, lineText: str) -> None:
        """
        Sets the that will be displayed in the first line of a toast
        """
        self.textFields[0] = lineText

    def SetSecondLine(self, lineText: str) -> None:
        """
        Sets the text that will be displayed in the second line of a toast
        """
        self.textFields[1] = lineText

    def SetThirdLine(self, lineText: str) -> None:
        """
        Sets the text that will be displayed in the third line of a toast
        """
        self.textFields[2] = lineText

    def AddAction(self, action: ToastButton) -> None:
        """
        Add an action to the action list. For example, if you're setting up a reminder,
        you would use 'action=remindlater&date=2020-01-20' as arguments. Maximum of five.

        :type action: ToastButton
        """
        if len(self.actions) + len(self.inputs) >= 5:
            warnings.warn(
                f"Cannot add action '{action.content}', you've already reached the maximum of five actions + inputs"
            )
            return

        self.actions.append(action)

    def AddImage(self, image: ToastDisplayImage) -> None:
        """
        Adds an the image that will be displayed on the toast, with a maximum of two (one as the logo and one large).
        Only works for ToastImageAndText classes

        :param image: :class:`ToastDisplayImage` to display in the toast
        """
        if len(self.images) >= 2:
            warnings.warn("The toast already has the maximum of two images.")

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

    def SetCustomTimestamp(self, notificationTime: Optional[datetime.datetime]) -> None:
        """
        Sets a custom notification timestamp. If you don't provide a custom timestamp,
        Windows uses the time that your notification was sent
        """
        self.timestamp = notificationTime

    def SetExpirationTime(self, expirationTime: Optional[datetime.datetime]) -> None:
        """
        Sets a time for the toast to expire on in the action center. If it is on-screen, nothing will happen
        """
        self.expiration_time = expirationTime

    def SetSuppressPopup(self, suppressPopup: bool) -> None:
        """
        Sets whether to suppress the popup and instead immediately place it in the action center
        """
        self.suppress_popup = suppressPopup

    def SetLaunchAction(self, launchAction: str) -> None:
        """
        Sets the protocol to launch when the toast is clicked
        """
        if not urllib.parse.urlparse(launchAction).scheme:
            warnings.warn(f"Ensure your launch action of {launchAction} is a proper protocol")

        self.launch_action = launchAction

    def clone(self) -> Toast:
        """
        Clone the current toast and return the new one

        :return: A deep copy of the toast
        :rtype: Toast
        """
        newToast = copy.deepcopy(self)
        newToast.tag = str(uuid.uuid4())

        return newToast