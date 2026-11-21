from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

from pytest import MonkeyPatch, fixture
from sybil import Sybil
from sybil.parsers.markdown import CodeBlockParser, PythonCodeBlockParser as MarkdownPythonCodeBlockParser
from sybil.parsers.rest import PythonCodeBlockParser, SkipParser


def pytest_addoption(parser):
    parser.addoption(
        "--real_run", action="store_true", default=False, help="Whether to actually display the notifications"
    )


# We used to just allow all the notifications to actually happen, but Windows doesn't like that
@fixture(scope="session", autouse=True)
def real_run_fixture(pytestconfig) -> Iterator[None]:
    if pytestconfig.getoption("real_run"):
        yield
    else:
        with (
            patch("winrt.windows.ui.notifications.ToastNotifier.show"),
            patch("winrt.windows.ui.notifications.ToastNotifier.add_to_schedule"),
            patch("winrt.windows.ui.notifications.ToastNotificationHistory.clear"),
            patch("time.sleep"),
        ):
            yield


@fixture
def docs_environment(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Accessible examples that don't require internet or user input
    """
    monkeypatch.chdir(tmp_path)
    # The custom audio example plays this file
    (tmp_path / "incoming_bloop.wav").touch()
    # The inline images example downloads an image, which only needs to exist since showing toasts is mocked
    monkeypatch.setattr("urllib.request.urlretrieve", lambda url, filename: Path(filename).touch())
    # Examples wait for Enter so their callbacks can run
    monkeypatch.setattr("builtins.input", lambda prompt="": "")


class PyconCodeBlockParser(MarkdownPythonCodeBlockParser):
    """
    Runs the doctests in ```pycon blocks
    """

    codeblock_parser_class = staticmethod(lambda _language, evaluator: CodeBlockParser("pycon", evaluator))


# Sybil doesn't use autouse fixtures, so request them by name
_docsFixtures = ["real_run_fixture", "docs_environment"]
pytest_collect_file = (
    Sybil(parsers=[PythonCodeBlockParser(), SkipParser()], path="docs", patterns=["*.rst"], fixtures=_docsFixtures)
    + Sybil(parsers=[PyconCodeBlockParser()], filenames=["README.md"], fixtures=_docsFixtures)
).pytest()
