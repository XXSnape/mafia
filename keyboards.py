from aiogram import types

from aiogram.utils.keyboard import InlineKeyboardBuilder

from keys import JOIN_CB, FINISH_REGISTRATION_CB


def get_join_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Присоединиться", callback_data=JOIN_CB)
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Начать игру", callback_data=FINISH_REGISTRATION_CB
        )
    )
    builder.adjust(1)
    return builder.as_markup()
