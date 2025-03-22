from aiogram import types, Bot
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cache.cache_types import LivePlayersIds
from keyboards.inline.cb.cb_text import (
    FINISH_REGISTRATION_CB,
    JOIN_CB,
)


async def get_join_kb(
    bot: Bot, game_chat: int, players_ids: LivePlayersIds
):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Присоединиться!",
            url=await create_start_link(
                bot, str(game_chat), encode=True
            ),
        )
    )
    if len(players_ids) >= 4:
        builder.add(
            types.InlineKeyboardButton(
                text="Начать игру",
                callback_data=FINISH_REGISTRATION_CB,
            )
        )
    builder.adjust(1)
    return builder.as_markup()
