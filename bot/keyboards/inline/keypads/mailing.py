from collections.abc import Iterable

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from cache.cache_types import Poisoned, GameCache, UsersInGame
from keyboards.inline.buttons.common import BACK_BTN

from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import (
    POLICEMAN_CHECKS_CB,
    POLICEMAN_KILLS_CB,
    WEREWOLF_TO_DOCTOR_CB,
    WEREWOLF_TO_MAFIA_CB,
    WEREWOLF_TO_POLICEMAN_CB,
    POISONER_POISONS_CB,
)


def send_transformation_kb(game_data: GameCache):
    from mafia.roles import (
        Mafia,
        MafiaAlias,
        Policeman,
        Doctor,
    )

    buttons = [
        InlineKeyboardButton(
            text=Policeman.role,
            callback_data=WEREWOLF_TO_POLICEMAN_CB,
        ),
        InlineKeyboardButton(
            text=Doctor.role, callback_data=WEREWOLF_TO_DOCTOR_CB
        ),
    ]
    if len(game_data[Mafia.roles_key]) + 1 < (
        len(game_data["live_players_ids"])
        - (len(game_data[Mafia.roles_key]) + 1)
    ):
        buttons.append(
            InlineKeyboardButton(
                text=MafiaAlias.role,
                callback_data=WEREWOLF_TO_MAFIA_CB,
            )
        )
    return generate_inline_kb(data_with_buttons=buttons)


def send_selection_to_players_kb(
    players_ids: list[int],
    players: UsersInGame,
    extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    exclude: Iterable[int] | int = (),
    user_index_cb: type[CallbackData] = UserActionIndexCbData,
):
    if isinstance(exclude, int):
        exclude = [exclude]
    buttons = [
        InlineKeyboardButton(
            text=players[str(player_id)]["full_name"],
            callback_data=user_index_cb(user_index=index).pack(),
        )
        for index, player_id in enumerate(players_ids)
        if player_id not in exclude
    ]
    buttons += extra_buttons
    return generate_inline_kb(data_with_buttons=buttons)


def selection_to_warden_kb(game_data: GameCache, user_id: int):
    checked = game_data["checked_for_the_same_groups"]
    buttons = []
    for player_id in game_data["live_players_ids"]:
        if player_id == user_id:
            continue
        text = game_data["players"][str(player_id)]["full_name"]
        if checked and player_id == checked[0][0]:
            text = "✅" + text
        buttons.append(
            InlineKeyboardButton(
                text=text, callback_data=str(player_id)
            )
        )
    return generate_inline_kb(data_with_buttons=buttons)


def kill_or_poison_kb(poisoned: Poisoned):
    buttons = [
        InlineKeyboardButton(
            text="Отравить💀", callback_data=POISONER_POISONS_CB
        ),
    ]
    if poisoned:
        buttons.append(
            InlineKeyboardButton(
                text="Убить☠️", callback_data=POLICEMAN_KILLS_CB
            )
        )
    return generate_inline_kb(data_with_buttons=buttons)


def kill_or_check_on_policeman():
    buttons = [
        InlineKeyboardButton(
            text="Проверить🔍",
            callback_data=POLICEMAN_CHECKS_CB,
        ),
        InlineKeyboardButton(
            text="Стрелять🔫",
            callback_data=POLICEMAN_KILLS_CB,
        ),
    ]
    return generate_inline_kb(data_with_buttons=buttons)


def choose_fake_role_kb(roles: list[tuple[str, str]]):
    buttons = [
        InlineKeyboardButton(text=role[0], callback_data=role[1])
        for role in roles
    ]
    buttons.append(BACK_BTN)
    return generate_inline_kb(data_with_buttons=buttons)
