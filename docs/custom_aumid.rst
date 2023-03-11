Custom AUMIDs
=====================

How to use
----------

When initialising :class:`~windows_toasts.windows_toasts.InteractableWindowsToaster`, pass the custom AUMID as notifierAUMID

Using an installed AUMID
------------------------
Microsoft.com has a page on `finding the Application User Model ID of an installed app <https://learn.microsoft.com/windows/configuration/find-the-application-user-model-id-of-an-installed-app>`_.
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
#. In the top address bar, paste :code:`HKEY_CURRENT_USER\Software\Classes\ActivatableClasses\Package`
#. Many Microsoft product AUMIDs should be listed, among others


Installing a custom AUMID
-------------------------
The library comes with two scripts: :code:`create_shell_link`, and :code:`register_hkey_aumid`, which can be run through the command line.

* :code:`create_shell_link` creates a null shortcut in the start menu folder
* :code:`register_hkey_aumid` registers a AUMID in the registry.

Both have the same final effect and the arguments can be understood using the --help argument.
Creating a shell link requires :code:`pywin32` to be installed, while registering in te registry requires it to be run with administrator access.