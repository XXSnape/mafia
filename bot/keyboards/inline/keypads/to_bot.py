from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_to_bot_kb(text="Ознакомиться с ролью"):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text=text, url="t.me/Drivenicebot"
        )
    )
    return builder.as_markup()
