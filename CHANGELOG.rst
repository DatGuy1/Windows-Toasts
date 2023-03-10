0.4.0 (2023-03-10)
=====
- Added Windows 11 and Python 3.12 classifiers

0.3.3 (2022-03-18)
======

- Fixed bug where user input would not work if there were no buttons
- register_hkey_aumi will now raise an error if supplied image is not a .ico file
- Added tests for user input and attribution text

0.3.2 (2022-03-18)
======

- Removed leftovers from older versions
- Added proper code style and enforcement
- Added tests to vastly increase coverage

0.3.1 (2022-03-11)
======

- Attribution text now only displays if using interactable toaster without a custom AUMI
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
- Add scripts to generate custom AUMIs for toasts
- Add tests for those scripts


0.1.3 (2022-02-19)
======

- Initial public release