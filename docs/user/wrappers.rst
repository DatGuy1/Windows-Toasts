Wrappers
========

Classes
-------

.. autosummary::
    windows_toasts.wrappers.ToastButtonColour
    windows_toasts.wrappers.ToastDuration
    windows_toasts.wrappers.ToastImagePosition
    windows_toasts.wrappers.ToastScenario
    windows_toasts.wrappers.ToastSystemButtonAction
    windows_toasts.wrappers.NotificationSetting
    windows_toasts.wrappers.ToastNotificationMode
    windows_toasts.wrappers.ToastImage
    windows_toasts.wrappers.ToastDisplayImage
    windows_toasts.wrappers.ToastProgressBar
    windows_toasts.wrappers.ToastInputTextBox
    windows_toasts.wrappers.ToastSelection
    windows_toasts.wrappers.ToastInputSelectionBox
    windows_toasts.wrappers.ToastButton
    windows_toasts.wrappers.ToastSystemButton
    windows_toasts.events.ToastActivatedEventArgs
    windows_toasts.events.ToastDismissalReason
    windows_toasts.events.ToastDismissedEventArgs
    windows_toasts.events.ToastFailedEventArgs

API
---

.. automodule:: windows_toasts.wrappers
    :exclude-members: ToastImage

    .. autoclass:: windows_toasts.wrappers.ToastImage

        .. automethod:: __init__

..
    This will probably go into another file soon

.. autoclass:: windows_toasts.events.ToastActivatedEventArgs

.. autoclass:: windows_toasts.events.ToastDismissalReason
    :exclude-members: USER_CANCELED, APPLICATION_HIDDEN, TIMED_OUT

.. autoclass:: windows_toasts.events.ToastDismissedEventArgs

.. autoclass:: windows_toasts.events.ToastFailedEventArgs
