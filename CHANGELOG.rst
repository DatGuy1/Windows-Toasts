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