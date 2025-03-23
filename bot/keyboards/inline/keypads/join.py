from operator import attrgetter

from aiogram import types, Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cache.cache_types import LivePlayersIds, RolesLiteral
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import CANCEL_BTN
from keyboards.inline.cb.cb_text import (
    FINISH_REGISTRATION_CB,
    CANCEL_CB,
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
    if len(players_ids) >= 1:  # TODO 4
        builder.add(
            types.InlineKeyboardButton(
                text="Начать игру",
                callback_data=FINISH_REGISTRATION_CB,
            )
        )
    builder.adjust(1)
    return builder.as_markup()


async def offer_to_place_bet(banned_roles: list[RolesLiteral]):
    buttons = []
    for key, role in get_data_with_roles().items():
        if key not in banned_roles:
            buttons.append(
                InlineKeyboardButton(
                    text=role.role, callback_data=key
                )
            )
    buttons.sort(key=attrgetter("text"))
    return generate_inline_kb(data_with_buttons=buttons)


def cancel_bet():
    return generate_inline_kb(data_with_buttons=[CANCEL_BTN])
