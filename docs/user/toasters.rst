Toasters
========

.. py:module:: windows_toasts.windows_toasts

.. autodoc2-docstring:: windows_toasts.windows_toasts
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`WindowsToaster <windows_toasts.windows_toasts.WindowsToaster>`
     - .. autodoc2-docstring:: windows_toasts.windows_toasts.WindowsToaster
          :summary:
   * - :py:obj:`InteractableWindowsToaster <windows_toasts.windows_toasts.InteractableWindowsToaster>`
     - .. autodoc2-docstring:: windows_toasts.windows_toasts.InteractableWindowsToaster
          :summary:

API
~~~

.. py:class:: WindowsToaster(applicationText: str)
   :canonical: windows_toasts.windows_toasts.WindowsToaster

   .. autodoc2-docstring:: windows_toasts.windows_toasts.WindowsToaster

   .. rubric:: Initialization

   .. autodoc2-docstring:: windows_toasts.windows_toasts.WindowsToaster.__init__

   .. py:method:: show_toast(toast: windows_toasts.toast_types.Toast) -> None
      :canonical: windows_toasts.windows_toasts.WindowsToaster.show_toast

.. py:class:: InteractableWindowsToaster(applicationText: str, notifierAUMID: typing.Optional[str] = None)
   :canonical: windows_toasts.windows_toasts.InteractableWindowsToaster

   .. autodoc2-docstring:: windows_toasts.windows_toasts.InteractableWindowsToaster

   .. rubric:: Initialization

   .. autodoc2-docstring:: windows_toasts.windows_toasts.InteractableWindowsToaster.__init__

   .. py:method:: show_toast(toast: windows_toasts.toast_types.Toast) -> None
      :canonical: windows_toasts.windows_toasts.InteractableWindowsToaster.show_toast
