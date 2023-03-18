import time
from typing import Iterator
from unittest.mock import patch

from pytest import fixture


# We used to just allow all the notifications to actually happen, but Windows doesn't like that
@fixture(scope="session", autouse=True)
def default_session_fixture(pytestconfig) -> Iterator[None]:
    if pytestconfig.getoption("real_run"):
        yield
    else:
        with patch("winsdk.windows.ui.notifications.ToastNotificationManager.create_toast_notifier"), patch(
            "winsdk.windows.ui.notifications.ToastNotifier.show"
        ), patch("winsdk.windows.ui.notifications.ToastNotificationHistory.clear"):
            yield


@fixture(scope="function", autouse=True)
def slow_down_tests(pytestconfig):
    yield
    if pytestconfig.getoption("real_run"):
        time.sleep(10)


def pytest_addoption(parser):
    parser.addoption(
        "--real_run", action="store_true", default=False, help="Whether to actually display the notifications"
    )
