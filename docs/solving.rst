Problem solving
===============

The notification platform is unavailable
----------------------------------------

If you are sending too many notifications within a short timespan, you may encounter the following exception:
``OSError: [WinError -2143420155] The notification platform is unavailable.``

You can solve this by either **rebooting**, or:

#. disabling the WpnUserService through services.msc or the task manager
#. deleting the ``%LOCALAPPDATA%\Microsoft\Windows\Notifications`` directory
#. restarting the aforementioned service, and possibly WpnService as well

The destructiveness of the latter process is undetermined. As always, rebooting the computer is the safest procedure.

Building with Nuitka
--------------------

pywinrt reads each Windows namespace from a ``_table.pywinrt`` file beside its module, and imports some of those modules
only once the program is running, the first time a call returns one of their types. Nuitka can't see either, so a
standalone build fails when importing Windows-Toasts, or later with
``ModuleNotFoundError: No module named 'winrt.windows.foundation.collections'``. To avoid both, include all of winrt and
its data files:

.. code-block:: shell

    python -m nuitka --mode=standalone --include-package=winrt --include-package-data=winrt your_script.py

PyInstaller doesn't need this, since pywinrt comes with a PyInstaller hook that does the same.
