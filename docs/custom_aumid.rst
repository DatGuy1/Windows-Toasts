Custom AUMIDs
=====================

Custom AUMIDs can be used to display user-defined titles and icons.
When initialising :class:`~windows_toasts.toasters.InteractableWindowsToaster`, pass the custom AUMID as notifierAUMID.

Installing a custom AUMID
-------------------------
Installing a custom AUMID allows you to use your own title, icon, and listen to activation after the notification was relegated to Action Center.

The library comes with a command to implement it, :code:`register_hkey_aumid`.
The arguments can be understood using the --help argument. If you have the Python Scripts directory in your path, you should be able to execute it by opening the command console and simply executing :code:`register_hkey_aumid`.
Otherwise, run it through Python with :code:`python -m windows_toasts.register_hkey_aumid`.

Using an installed AUMID
------------------------
Microsoft.com has a page on `finding the Application User Model ID of an installed app <https://learn.microsoft.com/windows/configuration/store/find-aumid>`_.
Below are the ways I recommend

Using Powershell
~~~~~~~~~~~~~~~~
You can use Powershell to view existing AUMIDs.

.. code-block:: powershell

    Get-StartApps

Will return a table of all applications installed for the current user, with the right row containing AUMIDs for each corresponding name.

Using the registry
~~~~~~~~~~~~~~~~~~

#. Open registry editor
#. In the top address bar, paste :code:`HKEY_CURRENT_USER\\Software\\Classes\\ActivatableClasses\\Package`
#. Many Microsoft product AUMIDs should be listed, among other third-party programs