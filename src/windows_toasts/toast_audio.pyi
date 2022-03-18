from enum import Enum
from typing import Union

class AudioSource(Enum):
    Default: str
    IM: str
    Mail: str
    Reminder: str
    SMS: str
    Alarm: str
    Alarm2: str
    Alarm3: str
    Alarm4: str
    Alarm5: str
    Alarm6: str
    Alarm7: str
    Alarm8: str
    Alarm9: str
    Alarm10: str
    Call: str
    Call2: str
    Call3: str
    Call4: str
    Call5: str
    Call6: str
    Call7: str
    Call8: str
    Call9: str
    Call10: str

class ToastAudio:
    sound: Union[AudioSource, str] = ...
    looping: bool = ...
    silent: bool = ...
    def __init__(self, sound: Union[AudioSource, str] = ..., looping: bool = ..., silent: bool = ...) -> None: ...
