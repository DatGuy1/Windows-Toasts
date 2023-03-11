Wrappers
========

Classes
-------

.. autodoc2-summary::
    windows_toasts.toast_types.ToastDuration
    windows_toasts.events.ToastActivatedEventArgs

API
---

.. autoenum:: windows_toasts.toast_types.ToastDuration

.. py:class:: ToastActivatedEventArgs
   :canonical: windows_toasts.events.ToastActivatedEventArgs

   .. autodoc2-docstring:: windows_toasts.events.ToastActivatedEventArgs

   .. py:attribute:: arguments
      :canonical: windows_toasts.events.ToastActivatedEventArgs.arguments
      :type: typing.Optional[str]
      :value: None

      .. autodoc2-docstring:: windows_toasts.events.ToastActivatedEventArgs.arguments

   .. py:attribute:: input
      :canonical: windows_toasts.events.ToastActivatedEventArgs.input
      :type: typing.Optional[str]
      :value: None

      .. autodoc2-docstring:: windows_toasts.events.ToastActivatedEventArgs.input

   .. py:method:: fromWinRt(eventArgs: winsdk._winrt.Object) -> windows_toasts.events.ToastActivatedEventArgs
      :canonical: windows_toasts.events.ToastActivatedEventArgs.fromWinRt
      :classmethod:

      .. autodoc2-docstring:: windows_toasts.events.ToastActivatedEventArgs.fromWinRt
