from aiogram.filters.callback_data import CallbackData
from cache.cache_types import StagesOfGameLiteral


class GroupSettingsCbData(CallbackData, prefix="set"):
    group_id: int


class TimeOfDayCbData(CallbackData, prefix="time"):
    stage_of_game: StagesOfGameLiteral
    seconds: int
