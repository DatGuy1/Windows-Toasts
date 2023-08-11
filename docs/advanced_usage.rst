Advanced usage
==============

What else can Windows-Toasts be used for? Since you're here, you probably already have your own idea, but here's a few examples:

Display an image
----------------

Lets try out displaying an image

.. code-block:: python

    from windows_toasts import Toast, ToastDisplayImage, WindowsToaster

    toaster = WindowsToaster('Windows-Toasts')

    newToast = Toast()
    newToast.SetFirstLine('<--- look, the Windows logo!')
    # str or PathLike
    newToast.AddImage(ToastDisplayImage.fromPath('C:/Windows/System32/@WLOGO_96x96.png'))

    toaster.show_toast(newToast)

.. note::
    When not using InteractableWindowsToaster you can display up to two images, and one of them must be marked as 'large'.

Open a website on click
-----------------------

We use :meth:`windows_toasts.toast.Toast.SetLaunchAction` to open a website when the notification is pressed.

.. code-block:: python

    import webbrowser
    from windows_toasts import Toast, WindowsToaster

    toaster = WindowsToaster('Rick Astley')

    newToast = Toast()
    newToast.SetFirstLine('Hello there! You just won a thousand dollars! Click me to claim it!')
    # Inline lambda function. This could also be an actual function
    newToast.SetLaunchAction('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

    # Send it
    toaster.show_toast(newToast)


Play different audio
--------------------

There is a list of available, out-of-the-box audio sources at :class:`windows_toasts.toast_audio.AudioSource`. Lets play the Windows IM sound looping until the notification is dismissed/expires.

.. code-block:: python

    from windows_toasts import AudioSource, Toast, ToastAudio, WindowsToaster

    toaster = WindowsToaster('Windows-Toasts')

    newToast = Toast()
    newToast.SetFirstLine('Ding ding! Ding ding! Ding ding!')
    newToast.SetAudio(ToastAudio(AudioSource.IM, looping=True))

    toaster.show_toast(newToast)

Progress bars
-------------

.. code-block:: python

    from windows_toasts import InteractableWindowsToaster, Toast, ToastProgressBar

    toaster = InteractableWindowsToaster('Windows-Toasts')

    # progress=None means the bar will be indeterminate
    progressBar = ToastProgressBar(
        'Preparing...', 'Python 4 release', progress=None, progress_override='? millenniums remaining'
    )

    newToast = Toast(progress_bar=progressBar)

    toaster.show_toast(newToast)

Dynamically modifying toast content
-----------------------------------

You can dynamically modify a toast's progress bar or text field

.. code-block:: python

    import time
    from windows_toasts import InteractableWindowsToaster, Toast, ToastProgressBar

    toaster = InteractableWindowsToaster('Python')

    newToast = Toast()
    newToast.SetFirstLine('Starting.')
    progressBar = ToastProgressBar('Waiting...', progress=0)
    newToast.SetProgressBar(progressBar)

    toaster.show_toast(newToast)

    for i in range(1, 11):
        time.sleep(1)
        progressBar.progress += 0.1
        newToast.SetFirstLine(f'Stage {i}')

        toaster.update_toast(newToast)

    newToast.SetFirstLine('Goodbye!')

    toaster.update_toast(newToast)

From Microsoft.com:

Since Windows 10, you could always replace a notification by sending a new toast with the same Tag and Group. So what's the difference between replacing the toast and updating the toast's data?

.. list-table:: Update or replace a notification
    :header-rows: 1

    * -
      - Replacing
      - Updating
    * - **Position in Action Center**
      - Moves the notification to the top of Action Center.
      - Leaves the notification in place within Action Center.
    * - **Modifying content**
      - Can completely change all content/layout of the toast
      - Can only change progress bar and top-level text
    * - **Reappearing as popup**
      - Can reappear as a toast popup if you leave :meth:`~windows_toasts.toast.Toast.SetSuppressPopup` set to false (or set to true to silently send it to Action Center)
      - Won't reappear as a popup; the toast's data is silently updated within Action Center
    * - **User dismissed**
      - Regardless of whether user dismissed your previous notification, your replacement toast will always be sent
      - If the user dismissed your toast, the toast update will fail

Scheduled toasts
----------------

You can also schedule a toast to display at a specified time

.. code-block:: python

    from datetime import datetime, timedelta
    from windows_toasts import WindowsToaster, Toast

    toaster = WindowsToaster('Python')

    displayTime = datetime.now() + timedelta(seconds=10)
    newToast = Toast(first_line=f'This will pop up at {displayTime}')

    toaster.schedule_toast(newToast, displayTime)

...and much more
----------------

See :class:`windows_toasts.toast.Toast` or the tests for more modifications you can make to toast notifications.