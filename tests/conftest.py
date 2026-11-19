import io
import math
import struct
import time
import wave
import zlib
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

from pytest import fixture


# We used to just allow all the notifications to actually happen, but Windows doesn't like that
@fixture(scope="session", autouse=True)
def real_run_fixture(pytestconfig) -> Iterator[None]:
    if pytestconfig.getoption("real_run"):
        yield
    else:
        with (
            patch("winrt.windows.ui.notifications.ToastNotificationManager.create_toast_notifier"),
            patch("winrt.windows.ui.notifications.ToastNotifier.show"),
            patch("winrt.windows.ui.notifications.ToastNotifier.add_to_schedule"),
            patch("winrt.windows.ui.notifications.ToastNotificationHistory.clear"),
            patch("time.sleep"),
        ):
            yield


def _make_png(width: int = 64, height: int = 64) -> bytes:
    """Build a small gradient PNG"""

    def chunk(chunkType: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + chunkType + data + struct.pack(">I", zlib.crc32(chunkType + data))

    rows = b"".join(
        b"\x00" + b"".join(bytes((x * 255 // width, y * 255 // height, 160)) for x in range(width))
        for y in range(height)
    )
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


def _make_wav(seconds: float = 1.0, frequency: int = 523, sampleRate: int = 22050) -> bytes:
    """Build a short, fading chime WAV"""

    def sample(index: int) -> int:
        elapsed = index / sampleRate
        # Fade in then decay
        envelope = min(1.0, elapsed / 0.01) * math.exp(-4 * elapsed)
        return int(6000 * envelope * math.sin(2 * math.pi * frequency * elapsed))

    frames = b"".join(struct.pack("<h", sample(index)) for index in range(int(seconds * sampleRate)))
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wavFile:
        wavFile.setnchannels(1)
        wavFile.setsampwidth(2)
        wavFile.setframerate(sampleRate)
        wavFile.writeframes(frames)

    return buffer.getvalue()


@fixture(scope="session")
def example_files_dir(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("example_files")


@fixture(scope="session")
def example_image_path(example_files_dir) -> Path:
    imagePath = example_files_dir / "image.png"
    imagePath.write_bytes(_make_png())
    return imagePath


@fixture(scope="session")
def example_audio_path(example_files_dir) -> Path:
    audioPath = example_files_dir / "audio.wav"
    audioPath.write_bytes(_make_wav())
    return audioPath


@fixture(scope="function", autouse=True)
def slow_down_tests(pytestconfig):
    yield
    if pytestconfig.getoption("real_run"):
        time.sleep(10)


def pytest_addoption(parser):
    parser.addoption(
        "--real_run", action="store_true", default=False, help="Whether to actually display the notifications"
    )
