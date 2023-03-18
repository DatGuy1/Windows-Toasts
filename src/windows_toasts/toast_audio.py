from dataclasses import dataclass
from enum import Enum
from typing import Union


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

    :param sound: Selected AudioSource to play
    :type sound: Union[AudioSource, str]
    :param looping: Whether the audio should loop once it ends. Stops abruptly when the notification is dismissed
    :type looping: bool
    :param silent: Silence any audio
    :type silent: bool
    """

    sound: Union[AudioSource, str] = AudioSource.Default
    looping: bool = False
    silent: bool = False

    @property
    def sound_value(self) -> str:
        """
        Returns the string value of the selected sound
        """
        if isinstance(self.sound, AudioSource):
            return self.sound.value
        else:
            return self.sound
