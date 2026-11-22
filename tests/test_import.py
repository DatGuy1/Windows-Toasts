from unittest.mock import patch

import pytest


def test_import_current():
    import importlib

    # Successful import
    import src.windows_toasts

    # 6.1.7601 = Windows 7
    with (
        patch("platform.version", return_value="6.1.7601"),
        pytest.raises(src.windows_toasts.UnsupportedOSVersionException),
    ):
        # Reload
        importlib.reload(src.windows_toasts)
