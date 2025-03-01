from aiogram.filters.callback_data import CallbackData


class UserIndexCbData(CallbackData, prefix="user"):
    user_index: int
