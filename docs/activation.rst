Activation and background buttons
=================================

Without an activator, your script only receives clicks on the toasts it showed since it started, through their :attr:`~windows_toasts.toast.Toast.on_activated`.
With the default AUMID, it stops receiving them once a toast has moved to Action Center. An activator is a COM class that Windows passes an AUMID's clicks to.
Registering one for your AUMID lets your script also receive:

* clicks on toasts your script showed before it restarted
* clicks on background buttons, which don't bring anything to the foreground and can keep the toast open while your script handles them
* clicks after your script has exited, if you also register a command for Windows to start it with

.. tip::
    If a click only has to open something, such as a website, a file or another app, you don't need an activator.
    Set the toast's :attr:`~windows_toasts.toast.Toast.launch_action`, or a button's :attr:`~windows_toasts.wrappers.ToastButton.launch`, to a URL or another protocol, and Windows opens it itself.
    That works from Action Center and after your script has exited, with any AUMID. See :ref:`launch-protocol`.

An activator needs your own :doc:`AUMID <custom_aumid>`, so it only works with :class:`~windows_toasts.toasters.InteractableWindowsToaster`.
Command Prompt's AUMID, which the toaster uses by default, can't have one.

.. _register-activator:

Registering an activator
------------------------

Register your AUMID with ``--activator``:

.. code-block:: console

    register_hkey_aumid --app_id MyName.MyApp --name "My App" --activator

Or from Python, with :func:`~windows_toasts.register_hkey_aumid.register_hkey`:

.. skip: next "Writes to the registry"

.. code-block:: python

    from windows_toasts.register_hkey_aumid import register_hkey

    register_hkey('MyName.MyApp', 'My App', activator=True)

To remove the AUMID and its activator, run ``register_hkey_aumid --app_id MyName.MyApp --remove``, or call :func:`~windows_toasts.register_hkey_aumid.unregister_hkey`.

Once the AUMID has an activator, a toaster using it starts listening for clicks when it shows a toast or you set its :attr:`~windows_toasts.toasters.InteractableWindowsToaster.on_activated`.
A click on a toast goes to the toast's own :attr:`~windows_toasts.toast.Toast.on_activated`.
Clicks on toasts your script didn't show in its current run, such as ones from before it restarted, go to the toaster's :attr:`~windows_toasts.toasters.InteractableWindowsToaster.on_activated` instead.
Both receive the toast's :attr:`~windows_toasts.events.ToastActivatedEventArgs.tag` and :attr:`~windows_toasts.events.ToastActivatedEventArgs.group`, so you can update or remove it.
A click on a :class:`~windows_toasts.wrappers.ToastHeader` in Action Center goes to the toaster's :attr:`~windows_toasts.toasters.InteractableWindowsToaster.on_activated`, with no tag or arguments, since a header belongs to every toast under it.

.. note::
    Only one process receives an activator's clicks at a time. If you run several copies of your script, or several scripts with the same AUMID, the others still get clicks on their own toasts, but not on background buttons.
    The first process receives every click on the others' toasts too, in its toaster's :attr:`~windows_toasts.toasters.InteractableWindowsToaster.on_activated`, so a click can be handled by both.

.. _activation-after-exit:

When your script isn't running
------------------------------

By default, clicking a toast while no process is listening does nothing.
To have Windows start your script to handle the click, pass the script to ``--activator``:

.. code-block:: console

    register_hkey_aumid --app_id MyName.MyApp --name "My App" --activator C:\path\to\my_app.py

This stores the command to start it in the registry.
A script is started with the ``pythonw.exe`` of the Python that ran ``register_hkey_aumid``, so no console window opens, which also means you won't see its output or errors.
A frozen executable, such as one built with Nuitka, is started as-is.

.. warning::
    Windows starts a new copy of your script from the beginning, with ``-Embedding`` added to its arguments, and passes it the click once it starts listening.
    The new copy didn't show the toast, so the click goes to the toaster's :attr:`~windows_toasts.toasters.InteractableWindowsToaster.on_activated`.
    When Windows starts your script, it has to set that and wait for the click, rather than doing what it normally does.

    Windows also starts a new copy if your script is running but hasn't started listening yet.
    Once it's listening, which showing a toast also starts, Windows gives it every click instead, including ones on toasts from earlier runs.
    So set the toaster's :attr:`~windows_toasts.toasters.InteractableWindowsToaster.on_activated` in every run, not just when Windows starts your script, or those clicks are lost.

The command stops working if your script or that Python moves, for example when you recreate a virtual environment, so register it again afterwards.
You can also call ``register_hkey('MyName.MyApp', 'My App', activator=Path(__file__))`` each time your script starts.
In a frozen executable, pass ``activator=Path(sys.executable)`` instead, since ``__file__`` isn't a real file there.
Don't register it with a ``register_hkey_aumid`` from a temporary or separate environment, such as the ones ``uvx`` and ``pipx`` create, which can disappear and won't have your script's other dependencies.

:func:`~windows_toasts.activation.launched_by_toast` tells you whether Windows started your script for a click.
Check it before parsing your own arguments, since they include ``-Embedding``.
Setting the toaster's :attr:`~windows_toasts.toasters.InteractableWindowsToaster.on_activated` starts listening, and the script has to keep running until the callback is done:

.. skip: next "Needs an AUMID registered with an activator"

.. code-block:: python

    import threading
    from windows_toasts import InteractableWindowsToaster, Toast, ToastActivatedEventArgs, ToastButton, launched_by_toast

    toaster = InteractableWindowsToaster('My App', 'MyName.MyApp')
    handled = threading.Event()

    def activated(activatedEventArgs: ToastActivatedEventArgs):
        print(activatedEventArgs.arguments, activatedEventArgs.inputs)
        handled.set()

    toaster.on_activated = activated

    if launched_by_toast():
        # A toast was clicked while the script wasn't running. Wait for the click to arrive
        handled.wait(timeout=30)
    else:
        toaster.show_toast(Toast(['Your report is ready'], actions=[ToastButton('Open', 'open')]))

.. _pending-update:

Background buttons and pending updates
--------------------------------------

A button with :attr:`~windows_toasts.wrappers.ToastButton.background` set is handled without bringing anything to the foreground.
With :attr:`~windows_toasts.wrappers.ToastButton.pending_update` too, the toast stays open in a pending state after the click, and Windows shows a loading animation on its buttons until you replace it.
To replace it, remove it with :meth:`~windows_toasts.toasters.BaseWindowsToaster.remove_toast`, then show a :class:`~windows_toasts.toast.Toast` with the same tag and group.
Both only need the tag and group the click carries, so they work even from a script Windows started for the click.
Wait about half a second after the click before removing it:

.. skip: next "Needs an AUMID registered with an activator"

.. code-block:: python

    import threading
    import time
    from windows_toasts import InteractableWindowsToaster, Toast, ToastActivatedEventArgs, ToastAudio, ToastButton, launched_by_toast

    toaster = InteractableWindowsToaster('My App', 'MyName.MyApp')
    handled = threading.Event()

    def activated(activatedEventArgs: ToastActivatedEventArgs):
        if activatedEventArgs.arguments == 'retry':
            clickTime = time.monotonic()
            # Retry the backup here
            # The user is already looking at the toast, so the replacement is silent
            finishedToast = Toast(['Backup finished', 'All your files are backed up'], tag=activatedEventArgs.tag, group=activatedEventArgs.group, audio=ToastAudio(silent=True))
            time.sleep(max(0, clickTime + 0.5 - time.monotonic()))
            # Removes the pending toast, which has the same tag and group
            toaster.remove_toast(finishedToast)
            toaster.show_toast(finishedToast)

        handled.set()

    toaster.on_activated = activated

    if launched_by_toast():
        handled.wait(timeout=30)
    else:
        # Run the backup here, and if it fails, ask whether to retry it
        backupToast = Toast(['Your backup failed', 'The drive was disconnected'], tag='backup', on_activated=activated)
        backupToast.AddAction(ToastButton('Retry', 'retry', background=True, pending_update=True))
        backupToast.AddAction(ToastButton('Ignore', 'ignore', background=True))
        toaster.show_toast(backupToast)
        handled.wait()

Neither :attr:`~windows_toasts.toast.Toast.suppress_popup` nor :meth:`~windows_toasts.toasters.BaseWindowsToaster.update_toast` ends the pending state of a toast that's on screen: they change its content, but its buttons keep loading until it times out.
If the toast was clicked in Action Center, the replacement pops up, since Action Center closes on the click.
