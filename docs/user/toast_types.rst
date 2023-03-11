Toast Types
====================================

See `ToastTemplateType on Microsoft.com <https://learn.microsoft.com/uwp/api/windows.ui.notifications.toasttemplatetype>`_

.. py:module:: windows_toasts.toast_types

.. autodoc2-docstring:: windows_toasts.toast_types
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Toast <windows_toasts.toast_types.Toast>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.Toast
          :summary:
   * - :py:obj:`ToastText1 <windows_toasts.toast_types.ToastText1>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.ToastText1
          :summary:
   * - :py:obj:`ToastText2 <windows_toasts.toast_types.ToastText2>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.ToastText2
          :summary:
   * - :py:obj:`ToastText3 <windows_toasts.toast_types.ToastText3>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.ToastText3
          :summary:
   * - :py:obj:`ToastText4 <windows_toasts.toast_types.ToastText4>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.ToastText4
          :summary:
   * - :py:obj:`ToastImageAndText1 <windows_toasts.toast_types.ToastImageAndText1>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.ToastImageAndText1
          :summary:
   * - :py:obj:`ToastImageAndText2 <windows_toasts.toast_types.ToastImageAndText2>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.ToastImageAndText2
          :summary:
   * - :py:obj:`ToastImageAndText3 <windows_toasts.toast_types.ToastImageAndText3>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.ToastImageAndText3
          :summary:
   * - :py:obj:`ToastImageAndText4 <windows_toasts.toast_types.ToastImageAndText4>`
     - .. autodoc2-docstring:: windows_toasts.toast_types.ToastImageAndText4
          :summary:

API
~~~

.. py:class:: Toast()
   :canonical: windows_toasts.toast_types.Toast

   .. autodoc2-docstring:: windows_toasts.toast_types.Toast

   .. autodoc2-docstring:: windows_toasts.toast_types.Toast.__init__

   .. py:attribute:: audio
      :canonical: windows_toasts.toast_types.Toast.audio
      :type: typing.Optional[windows_toasts.toast_audio.ToastAudio]
      :value: None

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.audio

   .. py:attribute:: duration
      :canonical: windows_toasts.toast_types.Toast.duration
      :type: typing.Literal[windows_toasts.toast_types.ToastDuration, windows_toasts.toast_types.ToastDuration, windows_toasts.toast_types.ToastDuration]
      :value: None

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.duration

   .. py:attribute:: on_activated
      :canonical: windows_toasts.toast_types.Toast.on_activated
      :type: typing.Optional[typing.Callable[[windows_toasts.events.ToastActivatedEventArgs], None]]
      :value: None

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.on_activated

   .. py:attribute:: on_dismissed
      :canonical: windows_toasts.toast_types.Toast.on_dismissed
      :type: typing.Optional[typing.Callable[[winsdk.windows.ui.notifications.ToastDismissedEventArgs], None]]
      :value: None

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.on_dismissed

   .. py:attribute:: on_failed
      :canonical: windows_toasts.toast_types.Toast.on_failed
      :type: typing.Optional[typing.Callable[[winsdk.windows.ui.notifications.ToastFailedEventArgs], None]]
      :value: None

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.on_failed

   .. py:method:: AddAction(actionName: str, actionArguments: str)
      :canonical: windows_toasts.toast_types.Toast.AddAction

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.AddAction

   .. py:method:: SetHeadline(headlineText: str) -> None
      :canonical: windows_toasts.toast_types.Toast.SetHeadline

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.SetHeadline

   .. py:method:: SetBody(bodyText: str) -> None
      :canonical: windows_toasts.toast_types.Toast.SetBody

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.SetBody

   .. py:method:: SetFirstLine(lineText: str) -> None
      :canonical: windows_toasts.toast_types.Toast.SetFirstLine

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.SetFirstLine

   .. py:method:: SetSecondLine(lineText: str) -> None
      :canonical: windows_toasts.toast_types.Toast.SetSecondLine

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.SetSecondLine

   .. py:method:: SetImage(imagePath: typing.Union[str, pathlib.Path]) -> None
      :canonical: windows_toasts.toast_types.Toast.SetImage

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.SetImage

   .. py:method:: SetInputField(placeholderText: str) -> None
      :canonical: windows_toasts.toast_types.Toast.SetInputField

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.SetInputField

   .. py:method:: SetCustomTimestamp(notificationTime: datetime.datetime) -> None
      :canonical: windows_toasts.toast_types.Toast.SetCustomTimestamp

      .. autodoc2-docstring:: windows_toasts.toast_types.Toast.SetCustomTimestamp

.. py:class:: ToastText1()
   :canonical: windows_toasts.toast_types.ToastText1

   .. autodoc2-docstring:: windows_toasts.toast_types.ToastText1

.. py:class:: ToastText2()
   :canonical: windows_toasts.toast_types.ToastText2

   .. autodoc2-docstring:: windows_toasts.toast_types.ToastText2

.. py:class:: ToastText3()
   :canonical: windows_toasts.toast_types.ToastText3

   .. autodoc2-docstring:: windows_toasts.toast_types.ToastText3

.. py:class:: ToastText4()
   :canonical: windows_toasts.toast_types.ToastText4

   .. autodoc2-docstring:: windows_toasts.toast_types.ToastText4

.. py:class:: ToastImageAndText1()
   :canonical: windows_toasts.toast_types.ToastImageAndText1

   .. autodoc2-docstring:: windows_toasts.toast_types.ToastImageAndText1

.. py:class:: ToastImageAndText2()
   :canonical: windows_toasts.toast_types.ToastImageAndText2

   .. autodoc2-docstring:: windows_toasts.toast_types.ToastImageAndText2

.. py:class:: ToastImageAndText3()
   :canonical: windows_toasts.toast_types.ToastImageAndText3

   .. autodoc2-docstring:: windows_toasts.toast_types.ToastImageAndText3

.. py:class:: ToastImageAndText4()
   :canonical: windows_toasts.toast_types.ToastImageAndText4

   .. autodoc2-docstring:: windows_toasts.toast_types.ToastImageAndText4
