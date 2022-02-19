# Windows-Toasts <a href="https://pypi.org/project/windows-toasts/" alt="PyPI version"><img src="https://img.shields.io/pypi/v/windows-toasts" /></a> <a href="https://pypi.org/project/windows-toasts/" alt="Supported Python versions"><img src="https://img.shields.io/pypi/pyversions/windows-toasts" /></a>

**Windows-Toasts** is a Python library used to send [toast notifications](https://docs.microsoft.com/en-us/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive-toasts) on Windows machines.

## Installation
Windows-Toasts supports Windows 10 and 11. While toasts do work on Windows 8.1 and below, Microsoft added features in Windows 10 that were never backported. 

Windows-Toasts is on PyPI:
```console
$ python -m pip install windows-toasts
``` 

## Usage

```python
>>> from windows_toasts import WindowsToaster, ToastText1
>>> wintoaster = WindowsToaster('Python')
>>> newToast = ToastText1()
>>> newToast.SetBody('Hello, world!')
>>> newToast.on_activated = lambda _: print('Toast clicked!')
>>> wintoaster.show_toast(newToast)
```

## But I already saw this package three times on PyPI!

I created this library since the other Windows toast notification libraries were all but abandoned, lacked features, and were using pywin32 bindings.

## Credits

The code is adapted from [mohabouje's wonderful C++ WinToasts library](https://github.com/mohabouje/WinToast)

Big thanks to dlech for his [recently created winrt fork](https://github.com/pywinrt/pywinrt)