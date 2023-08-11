Toast
====================================


Classes
-------

.. autosummary::
    windows_toasts.toast.ToastInput
    windows_toasts.toast.Toast

Data
----

.. autotypevar:: windows_toasts.toast.ToastInput

API
---

.. automodule:: windows_toasts.toast
    :exclude-members: Toast, ToastInput

    .. autoclass:: windows_toasts.toast.Toast()
        :exclude-members: audio, duration, scenario, textFields, timestamp, progress_bar, group, expiration_time,
                          suppress_popup, actions, images, inputs

        ..
            As this is the ''user'' reference, we skip all the internal use attributes. This may be changes in the future.

        .. automethod:: __init__
