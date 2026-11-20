Advanced usage
==============

What else can Windows-Toasts be used for? Since you're here, you probably already have your own idea, but here's a few examples:

Display an image
----------------

Let's try out displaying an image

.. code-block:: python

    from windows_toasts import Toast, ToastDisplayImage, WindowsToaster

    toaster = WindowsToaster('Windows-Toasts')

    newToast = Toast()
    newToast.text_fields = ['<--- look, the Windows logo!']
    # str or PathLike
    newToast.AddImage(ToastDisplayImage.fromPath('C:/Windows/System32/@WLOGO_96x96.png'))

    toaster.show_toast(newToast)

.. note::
    | When not using InteractableWindowsToaster you can display up to two images, and one of them must be marked as 'hero'.
    | A `hero image <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content#hero-image>`_ is an image that is prominently displayed at the top of the notification.

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

Out-of-the-box
^^^^^^^^^^^^^^
There is a list of available, out-of-the-box audio sources at :class:`windows_toasts.toast_audio.AudioSource`. Let's play the Windows IM sound looping until the notification is dismissed/expires.

.. code-block:: python

    from windows_toasts import AudioSource, Toast, ToastAudio, WindowsToaster

    toaster = WindowsToaster('Windows-Toasts')

    newToast = Toast()
    newToast.text_fields = ['Ding ding! Ding ding! Ding ding!']
    newToast.audio = ToastAudio(AudioSource.IM, looping=True)

    toaster.show_toast(newToast)

.. _custom-audio-files:

Custom files
^^^^^^^^^^^^
You can also play local audio files, with the following extensions:

* .aac
* .flac
* .m4a
* .mp3
* .wav
* .wma

.. code-block:: python

    from windows_toasts import Toast, ToastAudio, WindowsToaster
    from pathlib import Path

    toaster = WindowsToaster('Blooper')

    newToast = Toast()
    newToast.text_fields = ['Incoming bloop from', 'Steve']
    newToast.audio = ToastAudio(Path('incoming_bloop.wav'))

    toaster.show_toast(newToast)

.. warning::
    A warning will arise if local file does not exist, or if it uses an unsupported extension.
    This will make Windows play the default sound. There is no magic check for the file type – just its suffix.

    Additionally, some audio files will not work for seemingly no discernible reason. If this happens, the toast will be silent.

Windows doesn't read the file from your process. A sandboxed (AppContainer) process opens it, and if that process can't,
Windows plays the default sound without reporting an error. Files in your user folder or on other drives usually aren't
readable by sandboxed processes, while files in ``C:\Windows\Media`` are. Windows-Toasts doesn't check or change a
file's permissions.

To let sandboxed processes read a file, grant read access to ``ALL APPLICATION PACKAGES`` with
`icacls <https://learn.microsoft.com/windows-server/administration/windows-commands/icacls>`_ from a command prompt:

.. code-block:: console

    icacls notification_sound.wav /grant *S-1-15-2-1:(R)

Or through the file's properties:

#. Right-click the file and select **Properties**
#. Open the **Security** tab and click **Edit...**
#. Click **Add...**, enter ``ALL APPLICATION PACKAGES`` into the **Enter the object names to select** box, click
   **Check Names**, then **OK**
#. With ``ALL APPLICATION PACKAGES`` selected, make sure **Read** is allowed, then click **OK**

This lets every sandboxed app on the computer read the file, so don't do it for audio you'd rather keep private.

.. note::
    Microsoft's documentation lists absolute file paths as an unsupported source for custom audio, so this could stop
    working in a future version of Windows.

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

You can remove toasts, which will (if on-screen first hide them) and then immediately dismiss them from Action Center.

In the following example, the toast is automatically removed when it is dismissed to Action Center:

.. code-block:: python

    from windows_toasts import WindowsToaster, Toast

    toaster = WindowsToaster("Python")

    newToast = Toast(["Disappearing act"])
    newToast.on_dismissed = lambda _: toaster.remove_toast(newToast)

    toaster.show_toast(newToast)

.. warning::
    You can only remove toasts that were popped by a toaster with the same AUMID. Additionally, no exception will be thrown if the toast does not exist

Finding toasts in Action Center
-------------------------------

If you still have the :class:`~windows_toasts.toast.Toast` you showed, update or remove it directly. To reach a toast from a later run of your script, give it your own :attr:`~windows_toasts.toast.Toast.tag`, then create a :class:`~windows_toasts.toast.Toast` with the same tag and :attr:`~windows_toasts.toast.Toast.group` to update or remove it. An update can only change the text fields and progress bar the toast was shown with, and showing a toast with the same tag and group replaces the one in Action Center.

:meth:`~windows_toasts.toasters.BaseWindowsToaster.get_action_center_toasts` is only needed to check whether a toast is still in Action Center, or to read what it showed. For example, to avoid showing a reminder again while the last one is still there:

.. code-block:: python

    from windows_toasts import Toast, WindowsToaster

    toaster = WindowsToaster('Python')

    if not any(toast.tag == 'backup-failed' for toast in toaster.get_action_center_toasts()):
        toaster.show_toast(Toast(['Your backup failed'], tag='backup-failed'))

    # In a later run, once the backup succeeds
    toaster.remove_toast(Toast(tag='backup-failed'))

Each result is an :class:`~windows_toasts.toast.ActionCenterToast` rather than a :class:`~windows_toasts.toast.Toast`, since Windows only keeps part of the toast: its text fields and progress bar as it was shown, without changes from :meth:`~windows_toasts.toasters.BaseWindowsToaster.update_toast`. :class:`~windows_toasts.toasters.InteractableWindowsToaster`'s default AUMID is shared, so its list includes other programs' toasts too, which is why it's best to look for your own tags.

.. warning::
    Closing a toast's popup, even with its X, moves the toast into Action Center rather than deleting it. A toast is listed until the user clears it from Action Center, you remove it, or it expires, so being listed doesn't mean the user hasn't seen it.

Grouping toasts under a header
------------------------------

A :class:`~windows_toasts.wrappers.ToastHeader` shows related toasts together under one title in Action Center.

.. code-block:: python

    from windows_toasts import InteractableWindowsToaster, Toast, ToastHeader

    toaster = InteractableWindowsToaster('Python')

    header = ToastHeader('Reminders', launch='https://example.com/reminders')
    toaster.show_toast(Toast(['Drink some water'], header=header))
    toaster.show_toast(Toast(['Stretch your legs'], header=header))

Toasts are grouped by :attr:`~windows_toasts.wrappers.ToastHeader.header_id` alone, which defaults to the title, so toasts sent with the same title share a header even when they come from different runs of your script. If toasts with the same ``header_id`` have different titles, the header shows the most recent one's.

Clicking the header launches its :attr:`~windows_toasts.wrappers.ToastHeader.launch` protocol. Without one, clicking the header does nothing, and it doesn't trigger :attr:`~windows_toasts.toast.Toast.on_activated`.

To remove a header's toasts together, give them the same :attr:`~windows_toasts.toast.Toast.group` and use :meth:`~windows_toasts.toasters.BaseWindowsToaster.remove_toast_group`.

Placing images
------------------

Images can be placed in three different positions, as included in :attr:`windows_toasts.wrappers.ToastImagePosition`: Inline, hero, and AppLogo. Creating the :class:`~windows_toasts.wrappers.ToastDisplayImage` with:

* Inline – the image will be displayed inline, after any text elements, filling the full width of the visual area
* Hero – the image will be displayed prominently at the top of the notification
* AppLogo – the image will be displayed in a square on the left side of the visual area

Columns of styled text and images
---------------------------------

A :class:`~windows_toasts.adaptive.ToastGroup` adds a row of columns below the toast's text, each a :class:`~windows_toasts.adaptive.ToastSubgroup` of text and images. Unlike the text fields, :class:`~windows_toasts.adaptive.ToastText` can be styled, aligned and wrapped.

.. code-block:: python

    from windows_toasts import (
        InteractableWindowsToaster,
        Toast,
        ToastGroup,
        ToastSubgroup,
        ToastText,
        ToastTextAlign,
        ToastTextStyle,
    )

    toaster = InteractableWindowsToaster('Python')

    forecast = [('Mon', '18°'), ('Tue', '21°'), ('Wed', '16°')]
    columns = [
        ToastSubgroup(
            [
                ToastText(day, align=ToastTextAlign.Center),
                ToastText(temperature, ToastTextStyle.Subtitle, align=ToastTextAlign.Center),
            ],
            weight=1,
        )
        for day, temperature in forecast
    ]

    toaster.show_toast(Toast(['Weather', 'The next three days'], groups=[ToastGroup(columns)]))

.. note::
    Groups only show on :class:`~windows_toasts.toasters.InteractableWindowsToaster`. Their text can't be changed with :meth:`~windows_toasts.toasters.BaseWindowsToaster.update_toast`; show the toast again to change it. Windows also stops showing a group's content past a certain height, so keep each group to a few lines.

...and much more
----------------

See :class:`windows_toasts.toast.Toast` or the tests for more modifications you can make to toast notifications.