Advanced usage
==============

What else can Windows-Toasts be used for? Since you're here, you probably already have your own idea, but here's a few examples:

Display an image
----------------

:class:`ToastText1` isn't the only toast type that exists: there are four text notification types, and four text and image types. They are described at :doc:`/user/toast_types`.
Lets try out displaying an image

.. note::
    According to Microsoft, it should be possible to load online images, up to 3MB in size. However, I haven't gotten this to work. It is still supported and may work for you.

.. code-block:: python

    from windows_toasts import ToastImageAndText1, WindowsToaster

    toaster = WindowsToaster('Windows-Toasts')

    newToast = ToastImageAndText1()
    newToast.SetBody('<--- look, the Windows logo!')
    # str or PathLike
    newToast.SetImage('C:/Windows/System32/@WLOGO_96x96.png')

    toaster.show_toast(newToast)

Open a website on click
-----------------------

We use :meth:`windows_toasts.toast_types.Toast.on_activated` along with the built-in
`webbrowser <https://docs.python.org/3/library/webbrowser.html>`_ module to open a website
when the notification is pressed.

.. code-block:: python

    import webbrowser
    from windows_toasts import ToastText1, WindowsToaster

    toaster = WindowsToaster('Rick Astley')

    newToast = ToastText1()
    newToast.SetBody('Hello there! You just won a thousand dollars! Click me to claim it!')
    # Inline lambda function. This could also be an actual function
    newToast.on_activated = lambda _: webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

    # Send it
    toaster.show_toast(newToast)

.. note::
    Make sure your lambda/function takes an argument! The on_x fields pass data back to the callable. on_activated for instance returns :class:`ToastActivatedEventArgs`.

Play different audio
--------------------

There's a list of available, out-of-the-box audio sources at :class:`windows_toasts.toast_audio.AudioSource`. Lets play the Windows IM sound looping until the notification is dismissed/expires.

.. code-block:: python

    from windows_toasts import AudioSource, ToastAudio, ToastText1, WindowsToaster

    toaster = WindowsToaster('Windows-Toasts')

    newToast = ToastText1()
    newToast.SetBody('Ding ding! Ding ding! Ding ding!')
    newToast.audio = ToastAudio(AudioSource.IM, looping=True)

    toaster.show_toast(newToast)

...and more
-----------

See :class:`~windows_toasts.toast_types.Toast` for more modifications you can make to toast notifications.