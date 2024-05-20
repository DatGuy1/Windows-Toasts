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
    newToast.text_fields = ['<--- look, the Windows logo!']
    # str or PathLike
    newToast.AddImage(ToastDisplayImage.fromPath('C:/Windows/System32/@WLOGO_96x96.png'))

    toaster.show_toast(newToast)

.. note::
    When not using InteractableWindowsToaster you can display up to two images, and one of them must be marked as 'hero'.

Open a website on click
-----------------------

We use :attr:`windows_toasts.toast.Toast.launch_action` to open a website when the notification is pressed.

.. code-block:: python

    from windows_toasts import Toast, WindowsToaster

    toaster = WindowsToaster('Rick Astley')

    newToast = Toast()
    newToast.text_fields = ['Hello there! You just won a thousand dollars! Click me to claim it!']
    # Inline lambda function. This could also be an actual function
    newToast.launch_action = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

    # Send it
    toaster.show_toast(newToast)


Play different audio
--------------------

There is a list of available, out-of-the-box audio sources at :class:`windows_toasts.toast_audio.AudioSource`. Lets play the Windows IM sound looping until the notification is dismissed/expires.

.. code-block:: python

    from windows_toasts import AudioSource, Toast, ToastAudio, WindowsToaster

    toaster = WindowsToaster('Windows-Toasts')

    newToast = Toast()
    newToast.text_fields = ['Ding ding! Ding ding! Ding ding!']
    newToast.audio = ToastAudio(AudioSource.IM, looping=True)

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

    newToast = Toast(['Starting.'])
    progressBar = ToastProgressBar('Waiting...', progress=0)
    newToast.progress_bar = progressBar

    toaster.show_toast(newToast)

    for i in range(1, 11):
        time.sleep(1)
        progressBar.progress += 0.1
        newToast.text_fields = [f'Stage {i}']

        toaster.update_toast(newToast)

    newToast.text_fields = ['Goodbye!']

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
      - Can reappear as a toast popup if you leave :attr:`~windows_toasts.toast.Toast.suppress_popup` set to false (or set to true to silently send it to Action Center)
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
    newToast = Toast([f'This will pop up at {displayTime}'])

    toaster.schedule_toast(newToast, displayTime)

.. _system-actions:

Snoozing and dismissing
-----------------------

It is possible to snooze toasts and have them pop up later, as well as dismiss the toast entirely

.. code-block:: python

    from windows_toasts import InteractableWindowsToaster, Toast, ToastSystemButton, ToastSystemButtonAction, ToastInputSelectionBox, ToastSelection

    newToast = Toast(['Reminder', 'It\'s time to stretch!'])

    selections = (ToastSelection('1', '1 minute'), ToastSelection('2', '2 minutes'), ToastSelection('5', '5 minutes'))
    selectionBox = ToastInputSelectionBox(
        'snoozeBox', caption='Snooze duration', selections=selections, default_selection=selections[0]
    )
    newToast.AddInput(selectionBox)

    snoozeButton = ToastSystemButton(ToastSystemButtonAction.Snooze, 'Remind Me Later', relatedInput=selectionBox)
    dismissBox = ToastSystemButton(ToastSystemButtonAction.Dismiss)
    newToast.AddAction(snoozeButton)
    newToast.AddAction(dismissBox)

    InteractableWindowsToaster('Python').show_toast(newToast)

If you do not provide a caption, Windows will automatically use the appropriate localized strings.
If the :attr:`~windows_toasts.wrappers.ToastSystemButton.relatedInput` is None, the notification will snooze only once for a system-defined time interval. Otherwise, specifying a :class:`~windows_toasts.wrappers.ToastInputSelectionBox` allows the user to select a predefined snooze interval.

.. note::
    Ensure the :attr:`~windows_toasts.wrappers.ToastSelection.selection_id` is a positive integer, which represents the interval in minutes.

Removing toasts
---------------

You can remove toasts, which will (if on-screen first hide them) and then immediately dismiss them from the action center.

In the following example, the toast is automatically removed when it is dismissed to the action center:

.. code-block:: python

    from windows_toasts import WindowsToaster, Toast

    toaster = WindowsToaster("Python")

    newToast = Toast(["Disappearing act"])
    newToast.on_dismissed = lambda _: toaster.remove_toast(newToast)

    toaster.show_toast(newToast)

.. warning::
    You can only remove toasts that were popped by a toaster with the same AUMID. Additionally, no exception will be thrown if the toast does not exist

...and much more
----------------

See :class:`windows_toasts.toast.Toast` or the tests for more modifications you can make to toast notifications.