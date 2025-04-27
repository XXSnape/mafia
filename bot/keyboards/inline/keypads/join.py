from operator import attrgetter

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.deep_linking import create_start_link
from cache.cache_types import PlayersIds, RolesLiteral
from general import settings
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import CANCEL_BTN, TO_BOT_BTN, get_join_to_game_btn
from keyboards.inline.cb.cb_text import (
    FINISH_REGISTRATION_CB,
)


async def join_to_game_kb(
    bot: Bot, game_chat: int, players_ids: PlayersIds
):
    buttons = [
        await get_join_to_game_btn(bot=bot, game_chat=game_chat),
        TO_BOT_BTN,
    ]
    if len(players_ids) >= settings.mafia.minimum_number_of_players:
        buttons.append(
            InlineKeyboardButton(
                text="Начать игру",
                callback_data=FINISH_REGISTRATION_CB,
            )
        )
    return generate_inline_kb(data_with_buttons=buttons)

async def remind_about_joining_kb(bot: Bot, game_chat: int):
    btn = await get_join_to_game_btn(bot=bot, game_chat=game_chat)
    return generate_inline_kb(data_with_buttons=[btn])



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
    return generate_inline_kb(data_with_buttons=buttons, sizes=[2])


def cancel_bet():
    return generate_inline_kb(data_with_buttons=[CANCEL_BTN])
