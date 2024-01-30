class InvalidImageException(Exception):
    """The image provided was invalid"""


class ToastNotFoundError(Exception):
    """The toast could not be found"""


class UnsupportedOSVersionException(ImportError):
    """The operating system version is not supported"""
