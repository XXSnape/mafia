from aiogram.filters.callback_data import CallbackData


class GameNotificationCbData(CallbackData, prefix="reminders"):
    group_id: int
