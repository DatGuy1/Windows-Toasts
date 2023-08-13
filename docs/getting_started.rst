Getting started
===============

Installing Windows-Toasts
-------------------------

Windows-Toasts requires Python 3.8 or later, and supports Windows 10 and 11.

It can be installed using pip:

.. code-block:: shell

    $ python -m pip install windows-toasts

Install from source
~~~~~~~~~~~~~~~~~~~

The stable release version will most likely include the library's latest developments, but you can also install it directly from GitHub, where the code is
`hosted <https://github.com/DatGuy1/Windows-Toasts>`_.

First, clone the repository:

.. code-block:: shell

    $ git clone https://github.com/DatGuy1/Windows-Toasts.git

You can then embed it in your own Python package, or install it into your site-packages:

.. code-block:: shell

    $ cd Windows-Toasts
    $ python -m pip install .

Quickstart
------------

To display a toast notification:

.. code-block:: python

    # We import WindowsToaster and a toast format we want
    from windows_toasts import WindowsToaster, Toast
    # Prepare the toaster for bread (or your notification)
    toaster = WindowsToaster('Python')
    # Initialise the toast
    newToast = Toast()
    # Set the body of the notification
    newToast.text_fields = ['Hello, World!']
    # And display it!
    toaster.show_toast(newToast)
