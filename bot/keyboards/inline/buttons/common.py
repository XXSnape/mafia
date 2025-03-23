from aiogram.types import InlineKeyboardButton

from keyboards.inline.cb.cb_text import (
    PLAYER_BACKS_CB,
    ACTIONS_FOR_ROLES_CB,
    CANCEL_CB,
    SAVE_CB,
)

BACK_BTN = InlineKeyboardButton(
    text="Назад⬅️", callback_data=PLAYER_BACKS_CB
)

BACK_TO_SELECTING_ACTIONS_FOR_ROLES = InlineKeyboardButton(
    text="Назад⏪", callback_data=ACTIONS_FOR_ROLES_CB
)
CANCEL_BTN = InlineKeyboardButton(
    text="Отменить❌", callback_data=CANCEL_CB
)
SAVE_BTN = InlineKeyboardButton(
    text="Сохранить💾", callback_data=SAVE_CB
)
TO_BOT = InlineKeyboardButton(
    text="Сделать ставку!", url="t.me/Drivenicebot"
)
