"""
Toast activations through an activator, the COM class Windows passes an AUMID's activations to
"""

from __future__ import annotations

import sys
import threading
import time
import uuid
import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING, NamedTuple

from .events import ToastActivatedEventArgs
from .register_hkey_aumid import activator_clsid, read_activator_clsid

if TYPE_CHECKING:
    from .toast import Toast
    from .toasters import InteractableWindowsToaster

ActivatedCallback = Callable[[ToastActivatedEventArgs], None]

# We realistically won't reach this number, but have it as a safety check
_MAX_TOAST_CALLBACKS = 1000
# Debounce timer for how long a click delivered one way waits to arrive the other way
_DUPLICATE_SECONDS = 10

# Guards the dispatchers and their contents, which the toasters' threads and the activation threads share
_lock = threading.Lock()
_dispatchers: dict[uuid.UUID, _ActivationDispatcher] = {}


def launched_by_toast() -> bool:
    """
    Whether Windows started this process to deliver a toast activation, because nothing was listening for it.
    Windows adds ``-Embedding`` to the command line, so check this before parsing your own arguments.
    See :ref:`activation-after-exit`
    """
    return "-Embedding" in sys.argv[1:]


class _Click(NamedTuple):
    """What a click is told apart by. A click that arrives both ways has the same one each time"""

    tag: str | None
    group: str | None
    arguments: str | None
    inputs: dict[str, str]


class _Arrival(NamedTuple):
    """A click delivered one way, waiting to arrive the other way"""

    time: float
    fromActivator: bool
    click: _Click


class _ActivationDispatcher:
    """
    Hands an activator's clicks to their callbacks. A click on a toast this process showed goes to that toast's
    on_activated, and any other click to the on_activated of each toaster listening to the activator
    """

    def __init__(self) -> None:
        # None for a toast shown without an on_activated
        self._toastCallbacks: dict[tuple[str, str], ActivatedCallback | None] = {}
        # Toasters are kept alive while their on_activated is set, since they're there to receive activations
        self.toasters: set[InteractableWindowsToaster] = set()
        self._arrivals: list[_Arrival] = []

    def set_toast_callback(self, toast: Toast, callback: ActivatedCallback | None) -> None:
        key = (toast.tag, toast.group or toast.tag)
        with _lock:
            # Removed first, so showing a toast again makes it the newest
            self._toastCallbacks.pop(key, None)
            self._toastCallbacks[key] = callback
            if len(self._toastCallbacks) > _MAX_TOAST_CALLBACKS:
                # Forget the oldest toast. Its activations then go to the toasters' on_activated
                del self._toastCallbacks[next(iter(self._toastCallbacks))]

    def deliver_from_activator(self, arguments: str, inputs: dict[str, str]) -> None:
        """
        Deliver a click from the activator. The COM server calls this
        """
        self._deliver(ToastActivatedEventArgs._fromActivator(arguments, inputs), True)

    def deliver_activated(self, eventArgs: ToastActivatedEventArgs) -> None:
        """
        Deliver a click from the toast's Activated event
        """
        self._deliver(eventArgs, False)

    def _deliver(self, eventArgs: ToastActivatedEventArgs, fromActivator: bool) -> None:
        """
        Pass a click on the first time it arrives, and drop it when it arrives the other way. A click on a toast this
        process showed, on screen or in Action Center, arrives from the toast's Activated event, and from the
        activator too if this process registered the activator first. Clicks on background buttons, and on toasts
        this process didn't show, only arrive from the activator
        """
        click = _Click(eventArgs.tag, eventArgs.group, eventArgs.arguments, eventArgs.inputs or {})
        now = time.monotonic()
        with _lock:
            self._arrivals = [arrival for arrival in self._arrivals if now - arrival.time < _DUPLICATE_SECONDS]
            for i, arrival in enumerate(self._arrivals):
                if arrival.click == click and arrival.fromActivator != fromActivator:
                    del self._arrivals[i]
                    return

            self._arrivals.append(_Arrival(now, fromActivator, click))
            callback: ActivatedCallback | None = None
            shownHere = False
            if eventArgs.tag is not None:
                key = (eventArgs.tag, eventArgs.group or eventArgs.tag)
                shownHere = key in self._toastCallbacks
                callback = self._toastCallbacks.get(key)

            toasterCallbacks: list[ActivatedCallback] = []
            if callback is None:
                for toaster in self.toasters:
                    # Toasters that share a callback, such as ones made for each toast, call it only once. It's None
                    # if it's being unset
                    toasterCallback = toaster.on_activated
                    if toasterCallback is not None and toasterCallback not in toasterCallbacks:
                        toasterCallbacks.append(toasterCallback)

        if fromActivator and not shownHere and callback is None and not toasterCallbacks:
            # Windows gave the click to this process because it's listening, so it
            # won't start the activator's command for it
            warnings.warn(
                "A toast this process didn't show was clicked, but no toaster's on_activated is set to receive it",
                stacklevel=1,
            )

        # Called outside the lock, so the callbacks can show and update toasts
        if callback is not None:
            callback(eventArgs)

        for toasterCallback in toasterCallbacks:
            toasterCallback(eventArgs)


def _own_activator_clsid(appId: str) -> uuid.UUID | None:
    """
    The CLSID of the activator register_hkey registered for an AUMID. An activator registered some other way belongs to
    its own COM server, so it's left alone
    """
    clsid = activator_clsid(appId)
    return clsid if read_activator_clsid(appId) == clsid else None


def _listen(clsid: uuid.UUID, toaster: InteractableWindowsToaster | None = None) -> _ActivationDispatcher:
    """
    Start listening for an activator's activations, if this process isn't already

    :param toaster: A toaster to pass activations to, added before listening so it gets any that are waiting
    :raises OSError: If COM refuses to register the activator
    """
    # Only loaded once something uses an activator
    from . import _com_server

    with _lock:
        dispatcher = _dispatchers.get(clsid)
        if dispatcher is None:
            dispatcher = _dispatchers[clsid] = _ActivationDispatcher()
        if toaster is not None:
            dispatcher.toasters.add(toaster)

    _com_server.start_server(clsid, dispatcher.deliver_from_activator)
    return dispatcher


def _stop_delivering_to(toaster: InteractableWindowsToaster) -> None:
    with _lock:
        for dispatcher in _dispatchers.values():
            dispatcher.toasters.discard(toaster)
