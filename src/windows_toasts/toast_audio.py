import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Union

# According to https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/custom-audio-on-toasts
SUPPORTED_FILE_TYPES = [".aac", ".flac", ".m4a", ".mp3", ".wav", ".wma"]


class AudioSource(Enum):
    """
    Different audios built into Windows
    """

    Default = "Default"
    IM = "IM"
    Mail = "Mail"
    Reminder = "Reminder"
    SMS = "SMS"
    Alarm = "Looping.Alarm"
    Alarm2 = "Looping.Alarm2"
    Alarm3 = "Looping.Alarm3"
    Alarm4 = "Looping.Alarm4"
    Alarm5 = "Looping.Alarm5"
    Alarm6 = "Looping.Alarm6"
    Alarm7 = "Looping.Alarm7"
    Alarm8 = "Looping.Alarm8"
    Alarm9 = "Looping.Alarm9"
    Alarm10 = "Looping.Alarm10"
    Call = "Looping.Call"
    Call2 = "Looping.Call2"
    Call3 = "Looping.Call3"
    Call4 = "Looping.Call4"
    Call5 = "Looping.Call5"
    Call6 = "Looping.Call6"
    Call7 = "Looping.Call7"
    Call8 = "Looping.Call8"
    Call9 = "Looping.Call9"
    Call10 = "Looping.Call10"


@dataclass
class ToastAudio:
    """
    Audio configuration in a toast

    :param sound: Selected AudioSource or pathlib.Path to an audio file to play
    :type sound: Union[AudioSource, Path]
    :param looping: Whether the audio should loop continuously. Stops abruptly when the notification is dismissed
    :type looping: bool
    :param silent: Silence any audio
    :type silent: bool
    """

    sound: Union[AudioSource, Path] = AudioSource.Default
    looping: bool = False
    silent: bool = False

    @property
    def sound_value(self) -> str:
        """
        Returns the string value of the selected sound.
        Warns if using a non-existant file, or one which has a unsupported extension
        """
        if isinstance(self.sound, AudioSource):
            return f"ms-winsoundevent:Notification.{self.sound.value}"
        else:
            # We warn instead of erroring out because that's what Windows does, but I'm open to changing it
            if not self.sound.exists():
                warnings.warn(f"Custom audio file '{self.sound}' could not be found")
            if self.sound.suffix not in SUPPORTED_FILE_TYPES:
                warnings.warn(f"Custom audio file '{self.sound}' has unsupported extension '{self.sound.suffix}'")

            return self.sound.absolute().as_uri()
