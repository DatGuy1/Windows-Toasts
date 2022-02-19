from dataclasses import dataclass
from enum import Enum


class AudioSource(Enum):
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
    sound: AudioSource = AudioSource.Default
    looping: bool = False
    silent: bool = False

