0.4.0 (2023-03-18)
=====
- Added Windows 11 and Python 3.12 classifiers
- Merge typing back inline
- Dropped Python 3.7 support
- Changed scripts to use entry_points
- Created documentation on https://windows-toasts.readthedocs.io
- register_hkey_aumid no longer requires user to be an administrator
- Removed create_shell_link.py script
- Added many new features for toasts, including:
    - Initialising toasts with your data rather than setting it afterwards
    - Dynamically modifying toast content after its display
    - Multiple images in different slots
    - Scheduled toasts
    - Progress bars
    - Selection boxes input
    - Improved button configuration
    - Grouped toasts
    - Suppressing the popup
    - Toast expiration time
    - Toast scenarios
See the documentation for how to use them!

This release is mostly backwards compatible. The next release will be version 1.0.0, most likely be backwards incompatible, and will support on_activated callbacks after the toast has been relegated to the action center.

0.3.3 (2022-03-18)
======

- Fixed bug where user input would not work if there were no buttons
- register_hkey_aumid will now raise an error if supplied image is not a .ico file
- Added tests for user input and attribution text

0.3.2 (2022-03-18)
======

- Removed leftovers from older versions
- Added proper code style and enforcement
- Added tests to vastly increase coverage

0.3.1 (2022-03-11)
======

- Attribution text now only displays if using interactable toaster without a custom AUMID
- Fixed bug when binding on_activated without an input field

0.3.0 (2022-03-11)
======

- Renamed AddDuration to SetDuration
- Implemented text inputs fields. Use with SetInputField(placeholderText)
- Switched to using a first party ToastActivatedEventArgs class instead of WinRT's
- Added simple test to make sure toasts don't throw errors

0.2.0 (2022-02-26)
======

Major Revamp
------------

- Create InteractiveWindowsToaster, used for custom actions
- Move typing to .pyi stubs
- Add scripts to generate custom AUMIDs for toasts
- Add tests for those scripts


0.1.3 (2022-02-19)
======

- Initial public release