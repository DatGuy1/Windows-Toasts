1.1.1 (2024-05-19)
==================
- Allow setting attribution text (#140)

1.1.0 (2024-02-13)
==================
- Importing the module now throws an exception if the Windows version is unsupported (#122)
- Replaced toasts_winrt with winrt-Namespace packages (#113)
- Dropped Python 3.8 support (#113)

1.0.2 (2023-12-31)
===================
- Unquote image paths when the path contains characters that were escaped (#111)
- Convert image paths to absolute before converting to URI (#112)

1.0.1 (2023-09-11)
==================
- Fixed AttributeError when calling WindowsToaster.clear_toasts() (#96)
- unschedule_toast() now raise a ToastNotFoundError exception if the toast could not be found instead of warning (#97)

1.0.0 (2023-08-14)
==================
Major
-----
- Replaced winsdk requirement with toasts-winrt (#78)
- Removed toast templates in favour of ToastGeneric (#75)
- Simplified configuration of toasts (#82)

Minor
-----
- InvalidImageException is thrown when trying to add online images or images that do not exist
- Body is now the first argument for toasts
- Images no longer default to being circleCrop-ed
- Added support for inline images (#77)
- Added support for launching applications using their protocols (#80)
- Implemented snoozing and dismissing toasts (#83)

See the `migration guide <https://windows-toasts.readthedocs.io/en/latest/migration.html>`_.

0.4.1 (2023-04-20)
==================
- Recreated default Windows behaviour for progress bar. This allows it to be changed in the future while remaining faithful to the original implementation.
- Fixed AttributeError on WindowsToaster.clear_toasts()
- Bumped winsdk to 1.0.0b9

0.4.0 (2023-03-18)
==================
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

This release is mostly backwards compatible. The next *major* release will be version 1.0.0, most likely be backwards incompatible, and will support on_activated callbacks after the toast has been relegated to the action center.

0.3.3 (2022-03-18)
==================
- Fixed bug where user input would not work if there were no buttons
- register_hkey_aumid will now raise an error if supplied image is not a .ico file
- Added tests for user input and attribution text

0.3.2 (2022-03-18)
==================
- Removed leftovers from older versions
- Added proper code style and enforcement
- Added tests to vastly increase coverage

0.3.1 (2022-03-11)
==================
- Attribution text now only displays if using interactable toaster without a custom AUMID
- Fixed bug when binding on_activated without an input field

0.3.0 (2022-03-11)
==================
- Renamed AddDuration to SetDuration
- Implemented text inputs fields. Use with SetInputField(placeholderText)
- Switched to using a first party ToastActivatedEventArgs class instead of WinRT's
- Added simple test to make sure toasts don't throw errors

0.2.0 (2022-02-26)
==================

Major Revamp
------------
- Create InteractiveWindowsToaster, used for custom actions
- Move typing to .pyi stubs
- Add scripts to generate custom AUMIDs for toasts
- Add tests for those scripts


0.1.3 (2022-02-19)
==================
- Initial public release