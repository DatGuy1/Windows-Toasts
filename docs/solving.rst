Problem solving
===============

If you are sending too many notifications within a short timespan, you may encounter the following exception:
``OSError: [WinError -2143420155] The notification platform is unavailable.``

You can solve this by either **rebooting**, or:

#. disabling the WpnUserService through services.msc or the task manager
#. deleting the ``%LOCALAPPDATA%\Microsoft\Windows\Notifications`` directory
#. restarting the aforementioned service, and possibly WpnService as well

The destructiveness of the latter process is undetermined. As always, rebooting the computer is the safest procedure.