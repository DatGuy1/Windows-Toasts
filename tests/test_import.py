from pytest import raises
from unittest.mock import patch


# noinspection PyUnresolvedReferences
def test_import_current():
    import importlib

    # Successful import
    import src.windows_toasts

    # 6.1.7601 = Windows 7
    with patch("platform.version", return_value="6.1.7601"):
        with raises(src.windows_toasts.UnsupportedOSVersionException):
            # Reload
            importlib.reload(src.windows_toasts)
