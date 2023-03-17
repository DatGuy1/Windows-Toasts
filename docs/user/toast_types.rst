Toast Types
====================================

See `ToastTemplateType on Microsoft.com <https://learn.microsoft.com/uwp/api/windows.ui.notifications.toasttemplatetype>`_

Classes
-------

.. autosummary::
    windows_toasts.toast_types.ToastInput
    windows_toasts.toast_types.Toast
    windows_toasts.toast_types.ToastText1
    windows_toasts.toast_types.ToastText2
    windows_toasts.toast_types.ToastText3
    windows_toasts.toast_types.ToastText4
    windows_toasts.toast_types.ToastImageAndText1
    windows_toasts.toast_types.ToastImageAndText2
    windows_toasts.toast_types.ToastImageAndText3
    windows_toasts.toast_types.ToastImageAndText4

Data
----

.. autotypevar:: windows_toasts.toast_types.ToastInput

API
---

.. automodule:: windows_toasts.toast_types
    :exclude-members: Toast, ToastInput

    .. autoclass:: windows_toasts.toast_types.Toast()
        :exclude-members: audio, duration, scenario, textFields, timestamp, progress_bar, group, expiration_time,
                          suppress_popup, actions, images, inputs

        ..
            As this is the ''user'' reference, we skip all the internal use attributes. This may be changes in the future.

        .. automethod:: __init__
