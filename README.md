# Windows-Toasts [![PyPI version](https://img.shields.io/pypi/v/windows-toasts)](https://pypi.org/project/windows-toasts/) [![Supported Python versions](https://img.shields.io/pypi/pyversions/windows-toasts)](https://pypi.org/project/windows-toasts/) [![Downloads](https://pepy.tech/badge/windows-toasts/month)](https://pepy.tech/project/windows-toasts) [![codecov](https://codecov.io/gh/DatGuy1/Windows-Toasts/branch/master/graph/badge.svg?token=ZD8OF2SF61)](https://codecov.io/gh/DatGuy1/Windows-Toasts)

**Windows-Toasts** is a Python library used to send [toast notifications](https://docs.microsoft.com/en-us/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive-toasts) on Windows machines.

## Installation
Windows-Toasts supports Windows 10 and 11. While toast notifications do work on Windows 8.1 and below, Microsoft added features in Windows 10 that were never backported. 

Windows-Toasts is available through PyPI:
```console
$ python -m pip install windows-toasts
``` 

## Usage

Simple usage:

```python
>>> from windows_toasts import WindowsToaster, ToastText1
>>> wintoaster = WindowsToaster('Python')
>>> newToast = ToastText1()
>>> newToast.SetBody('Hello, world!')
>>> newToast.on_activated = lambda _: print('Toast clicked!')
>>> wintoaster.show_toast(newToast)
```

Proper documentation is in progress, but meanwhile you can take inspiration from the tests in tests/test_toasts.py.

## But I already saw this package three times on PyPI!

I created this library since the other Windows toast notification libraries were all but abandoned, lacked features, and were using pywin32 bindings.

Using WinRT may come with its own limitations. However, the only issue I've encountered compared to using pywin32 bindings is not being able to select the duration in seconds, but rather as short/long.

## Credits

The code is adapted from [mohabouje's wonderful C++ WinToasts library](https://github.com/mohabouje/WinToast)

Big thanks to dlech for his [recently created winrt fork](https://github.com/pywinrt/pywinrt)