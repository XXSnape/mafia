from aiogram.filters.callback_data import CallbackData


class GroupSettingsCbData(CallbackData, prefix="set"):
    group_id: int
    apply_own: bool
