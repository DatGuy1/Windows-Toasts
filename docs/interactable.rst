Interactable toasts
===================

Interactable toasts are toast notifications that lets the user interact with them, be it through different buttons or input fields.

Usage
-----
We import :class:`~windows_toasts.toasters.InteractableWindowsToaster` instead of :class:`~windows_toasts.windows_toasts.WindowsToaster`, but the rest is mostly the same. Here's a basic example:

.. code-block:: python

    from windows_toasts import InteractableWindowsToaster, Toast, ToastActivatedEventArgs, ToastButton

    interactableToaster = InteractableWindowsToaster('Questionnaire')
    newToast = Toast(['How are you?'])

    # Add two actions (buttons)
    newToast.AddAction(ToastButton('Decent', 'response=decent'))
    newToast.AddAction(ToastButton('Not so good', 'response=bad'))

    # Display it like usual
    interactableToaster.show_toast(newToast)

And we have buttons! We can't do much with them though, at least until we use on_activated.

.. code-block:: python

    def activated_callback(activatedEventArgs: ToastActivatedEventArgs):
        print(activatedEventArgs.arguments) # response=decent/response=bad

    newToast.on_activated = activated_callback

.. note::
    To make sure the activation of the toast triggeres the callback following its relegation to the action center, you must use a `custom AUMID <Creating a custom AUMID>`_.

Input fields
~~~~~~~~~~~~

Windows-Toasts also supports using text fields and selection boxes.

.. code-block:: python

    from windows_toasts import InteractableWindowsToaster, Toast, ToastInputTextBox, ToastInputSelectionBox, ToastSelection

    interactableToaster = InteractableWindowsToaster('Questionnaire')
    newToast = Toast(['Please enter your details'])

    # A text input field asking the user for their name
    newToast.AddInput(ToastInputTextBox('name', 'Your name', 'Barack Obama'))

    # Create three selections: Male, female, other, and prefer not to say
    toastSelections = (ToastSelection('male', 'Male'), ToastSelection('female', 'Female'), ToastSelection('other', 'Other'), ToastSelection('unknown', 'Prefer not to say'))
    # Initialise the selection box with a caption 'What is your gender?'. The selections are passed in, and it defaults to 'prefer not to say.'
    selectionBoxInput = ToastInputSelectionBox('gender', 'What is your gender?', toastSelections, default_selection=toastSelections[3])
    newToast.AddInput(selectionBoxInput)

    # For example: {'name': 'John Smith', 'gender': 'male'}
    newToast.on_activated = lambda activatedEventArgs: print(activatedEventArgs.inputs)

    interactableToaster.show_toast(newToast)

In this case, the on_activated callback will be executed when the user presses on the notification.

Combining the two
~~~~~~~~~~~~~~~~~

We can combine the two and a submit button

.. code-block:: python
    :emphasize-lines: 7,8

    from windows_toasts import InteractableWindowsToaster, Toast

    interactableToaster = InteractableWindowsToaster('Questionnaire')
    newToast = Toast()

    newToast.text_fields = ['What\'s your name?']
    newToast.AddInput(ToastInputTextBox('name', 'Your name', 'Barack Obama'))
    newToast.AddAction(ToastButton('Submit', 'submit'))
    newToast.on_activated = lambda activatedEventArgs: print(activatedEventArgs.input)

    interactableToaster.show_toast(newToast)

Caveats
-------

You may have noticed something weird when testing the above code. Why, when we display the toast, does it say command prompt in the top left, and have the icon for it?
InteractableWindowsToaster requires an Application User Model ID (AUMID) to function properly.
The package provides the command prompt as the default, and the applicationText becomes the :meth:`attribution text <windows_toasts.toast_document.ToastDocument.SetAttributionText>`.

You can choose between staying with the default command prompt AUMID, `finding another one <Using an installed AUMID>`_, or `creating your own <Creating a custom AUMID>`_.
