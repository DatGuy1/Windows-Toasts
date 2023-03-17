Interactable toasts
===================

Interactable toasts are toast notifications that lets the user interact with them, be it through different buttons or input fields.

Usage
-----
We import :class:`~windows_toasts.toasters.InteractableWindowsToaster` instead of :class:`~windows_toasts.windows_toasts.WindowsToaster`, but the rest is mostly the same. Here's a basic example:

.. code-block:: python

    from windows_toasts import InteractableWindowsToaster, ToastText1

    interactableToaster = InteractableWindowsToaster('Questionnaire')
    newToast = ToastText1()

    newToast.SetBody('How are you?')
    # Add two actions (buttons)
    newToast.AddAction('Decent', 'response=decent')
    newToast.AddAction('Not so good', 'response=bad')

    # Display it like usual
    interactableToaster.show_toast(newToast)

And we have buttons! We can't do much with them though, at least until we use on_activated.

.. code-block:: python

    def activated_callback(activatedEventArgs: ToastActivatedEventArgs):
        print(activatedEventArgs.arguments) # response=decent/response=bad

    newToast.on_activated = activated_callback

Input fields
~~~~~~~~~~~~

Windows-Toasts also supports using input fields.

.. code-block:: python

    from windows_toasts import InteractableWindowsToaster, ToastText1

    interactableToaster = InteractableWindowsToaster('Questionnaire')
    newToast = ToastText1()

    newToast.SetBody('What\'s your name?')
    newToast.SetInputField('Barack Obama')
    newToast.on_activated = lambda activatedEventArgs: print(activatedEventArgs.input)

    interactableToaster.show_toast(newToast)

In this case, the on_activated callback will be executed when the user presses on the notification.

Combining the two
~~~~~~~~~~~~~~~~~

We can combine the two and a submit button

.. code-block:: python
    :emphasize-lines: 7,8

    from windows_toasts import InteractableWindowsToaster, ToastText1

    interactableToaster = InteractableWindowsToaster('Questionnaire')
    newToast = ToastText1()

    newToast.SetBody('What\'s your name?')
    newToast.SetInputField('Barack Obama')
    newToast.AddAction('Submit', 'submit')
    newToast.on_activated = lambda activatedEventArgs: print(activatedEventArgs.input)

    interactableToaster.show_toast(newToast)

Caveats
-------

You may have noticed something weird in the code above. Why, when we display the toast, does it say command prompt in the top left, and have the icon for it?
InteractableWindowsToaster requires an Application User Model ID (AUMID) to function properly.
The package provides the command prompt as the default, and the applicationText becomes the :meth:`attribution text <windows_toasts.toast_document.ToastDocument.SetAttributionText>`.

You can choose between staying with the default command prompt AUMID, `finding another one <Using an installed AUMID>`_, or `creating your own <Creating a custom AUMID>`_.