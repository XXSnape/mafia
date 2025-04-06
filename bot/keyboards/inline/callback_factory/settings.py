from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData


class TimeOfDay(IntEnum):
    day = auto()
    night = auto()


class GroupSettingsCbData(CallbackData, prefix="set"):
    group_id: int
    apply_own: bool


class TimeOfDayCbData(CallbackData, prefix="time"):
    time_of_day: TimeOfDay
    seconds: int
