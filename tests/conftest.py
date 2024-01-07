import time
from typing import Iterator
from unittest.mock import patch

from pytest import fixture


# We used to just allow all the notifications to actually happen, but Windows doesn't like that
@fixture(scope="session", autouse=True)
def real_run_fixture(pytestconfig) -> Iterator[None]:
    if pytestconfig.getoption("real_run"):
        yield
    else:
        with patch("winrt.windows.ui.notifications.ToastNotificationManager.create_toast_notifier"), patch(
            "winrt.windows.ui.notifications.ToastNotifier.show"
        ), patch("winrt.windows.ui.notifications.ToastNotificationHistory.clear"):
            yield


@fixture(scope="session", autouse=True)
def download_example_image():
    # Download an example image and delete it at the end
    import urllib.request
    from pathlib import Path

    # Save the image to pythong.png
    imageUrl = "https://www.python.org/static/community_logos/python-powered-h-140x182.png"
    imagePath = Path.cwd() / "python.png"
    urllib.request.urlretrieve(imageUrl, imagePath)

    yield

    imagePath.unlink()


@fixture
def example_image_path():
    from pathlib import Path

    return Path.cwd() / "python.png"


@fixture(scope="function", autouse=True)
def slow_down_tests(pytestconfig):
    yield
    if pytestconfig.getoption("real_run"):
        time.sleep(10)


def pytest_addoption(parser):
    parser.addoption(
        "--real_run", action="store_true", default=False, help="Whether to actually display the notifications"
    )
