from aiogram.types import InlineKeyboardButton

from general import settings
from general.text import TO_SAVE
from keyboards.inline.cb.cb_text import (
    PLAYER_BACKS_CB,
    ACTIONS_FOR_ROLES_CB,
    CANCEL_CB,
    SAVE_CB,
    HELP_CB,
)

BACK_BTN = InlineKeyboardButton(
    text="Назад⬅️", callback_data=PLAYER_BACKS_CB
)

BACK_TO_SELECTING_ACTIONS_FOR_ROLES_BTN = InlineKeyboardButton(
    text="Назад⏪", callback_data=ACTIONS_FOR_ROLES_CB
)
CANCEL_BTN = InlineKeyboardButton(
    text="❌Отменить", callback_data=CANCEL_CB
)
SAVE_BTN = InlineKeyboardButton(text=TO_SAVE, callback_data=SAVE_CB)
TO_BOT_BTN = InlineKeyboardButton(
    text="Сделать ставку!",
    url=settings.bot.url,
)
HELP_BTN = InlineKeyboardButton(
    text="🆘Помощь", callback_data=HELP_CB
)
ADD_BOT_TO_GROUP = InlineKeyboardButton(
    text="Добавить в группу👥",
    url=f"https://{settings.bot.url}?startgroup&admin=post_messages+"
    f"delete_messages+"
    f"restrict_members+pin_messages",
)
