Migrating from v0.x to v1.0.0
=============================

Version 1.0.0 comes with a large backend refactoring and simplification of existing features, along with a few new features.
This guide will detail the changes and how to adapt to them.

Replaced winsdk requirement with toasts-winrt
---------------------------------------------
Instead of the 12 MB `winsdk <https://pypi.org/project/winsdk/>`_ release, Windows-Toasts now uses a streamlined 500 kB `toasts-winrt <https://pypi.org/project/toasts-winrt/>`_ package to lessen install times and storage requirements.

Toast class simplification
--------------------------
Toasts no longer require a ToastType, but are rather initialised with just :class:`windows_toasts.toast.Toast`.

In addition, all of the SetX methods have been removed in favour of directly modifying the attributes (the AddX methods remain for now).
Set[Headline/Body/FirstLine/SecondLine] is now a list named :attr:`~windows_toasts.toast.Toast.text_fields`. Instead of using :code:`SetDuration()` and the like, just set it directly: :code:`toast.duration = ToastDuration.Short`.

For instance,

Here is how you would configure toasts before:

.. code-block:: python

    from windows_toasts import WindowsToaster, ToastDuration

    from windows_toasts import ToastText2

    toast = ToastText2()

    toast.SetHeadline('Hello,')
    toast.SetBody('World!')

    toast.SetDuration(ToastDuration.Short)

    WindowsToaster('Python').show_toast(toast)

Here's how you would do it now:

.. code-block:: python

    from windows_toasts import WindowsToaster, ToastDuration

    from windows_toasts import Toast

    toast = Toast()

    toast.text_fields = ['Hello', 'World!']
    # Or, directly, toast = Toast(['Hello', 'World!'])

    toast.duration = ToastDuration.short

    WindowsToaster('Python').show_toast(toast)

and here's the highlighted difference between the two:

.. code-block:: diff

    from windows_toasts import WindowsToaster, ToastDuration

    - from windows_toasts import ToastText2
    + from windows_toasts import Toast

    - toast = ToastText2()
    + toast = Toast()

    - toast.SetHeadline('Hello,')
    - toast.SetBody('World!')
    + toast.text_fields = ['Hello', 'World!']

    - toast.SetDuration(ToastDuration.Short)
    + toast.duration = ToastDuration.short

    WindowsToaster('Python').show_toast(toast)


New features
------------

Release v1.0.0 also arrives with a few new features

Launching through protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For applications that support protocols, you can now make your toasts and buttons launch that protocol directly.

.. code-block:: python

    from windows_toasts import InteractableWindowsToaster, Toast, ToastButton

    protocol_toast = Toast(['Click the toast to launch google.com', 'or, alternatively'], launch_action='https://google.com')

    bing_button = ToastButton('Launch Bing', launch='https://bing.com')
    baidu_button = ToastButton('Launch Baidu', launch='https://baidu.com')

    protocol_toast.AddAction(bing_button)
    protocol_toast.AddAction(baidu_button)

    InteractableWindowsToaster('Browser Launcher').show_toast(protocol_toast)

.. note::
    Web browsers are not the only thing you can launch with protocols.
    Set :attr:`windows_toasts.wrappers.ToastButton.launch` to ``spotify:playlist:37i9dQZEVXbMDoHDwVN2tF`` to launch the Spotify client on the global Top 50, set it to ``steam://friends/status/offline`` to set yourself offline on the Steam client, et cetera.

Inline images
^^^^^^^^^^^^^

Images have been reworked, with the :class:`windows_toasts.wrappers.ToastImagePosition` enum introducted as to make it possible to display more than two.

.. code-block:: python

    # Downloads the Python logo
    import urllib.request
    from pathlib import Path

    # Save the image to python.png
    image_url = 'https://www.python.org/static/community_logos/python-powered-h-140x182.png'
    image_path = Path.cwd() / 'python.png'
    urllib.request.urlretrieve(image_url, image_path)

    from windows_toasts import InteractableWindowsToaster, Toast, ToastDisplayImage, ToastImage, ToastImagePosition
    toast_image_python = ToastImage(image_path)

    toast_images = [
        ToastDisplayImage(toast_image_python, position=ToastImagePosition.Hero),
        ToastDisplayImage(toast_image_python, position=ToastImagePosition.AppLogo),
        ToastDisplayImage(toast_image_python, position=ToastImagePosition.Inline),
        ToastDisplayImage(toast_image_python, position=ToastImagePosition.Inline)
    ]
    new_toast = Toast(text_fields=['Hiss!'], images=toast_images)

    InteractableWindowsToaster('Python').show_toast(new_toast)

System actions
^^^^^^^^^^^^^^

There is a writeup on how to use the snooze and dismiss system actions in the :ref:`system-actions` section