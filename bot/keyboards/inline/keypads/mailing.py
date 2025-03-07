from collections.abc import Iterable
from typing import TYPE_CHECKING

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton


if TYPE_CHECKING:
    from cache.cache_types import UsersInGame, Roles
    from cache.cache_types import GameCache
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import (
    POLICEMAN_CHECKS_CB,
    POLICEMAN_KILLS_CB,
    PLAYER_BACKS_CB,
    WEREWOLF_TO_POLICEMAN_CB,
    WEREWOLF_TO_DOCTOR_CB,
    WEREWOLF_TO_MAFIA_CB,
)


def send_transformation_kb(game_data: "GameCache"):
    buttons = [
        InlineKeyboardButton(
            text="Маршал", callback_data=WEREWOLF_TO_POLICEMAN_CB
        ),
        InlineKeyboardButton(
            text="Доктор", callback_data=WEREWOLF_TO_DOCTOR_CB
        ),
    ]
    if len(game_data["mafias"]) + 1 < (
        len(game_data["players_ids"])
        - (len(game_data["mafias"]) + 1)
    ):
        buttons.append(
            InlineKeyboardButton(
                text="Мафия", callback_data=WEREWOLF_TO_MAFIA_CB
            )
        )
    return generate_inline_kb(data_with_buttons=buttons)


def send_selection_to_players_kb(
    players_ids: list[int],
    players: "UsersInGame",
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


def choose_fake_role_kb(roles: list["Roles"]):
    buttons = [
        InlineKeyboardButton(
            text=role.value.role, callback_data=role.name
        )
        for role in roles
    ]
    buttons.append(POLICEMAN_BACK_BTN)
    return generate_inline_kb(data_with_buttons=buttons)


POLICEMAN_BACK_BTN = InlineKeyboardButton(
    text="Назад⬅️", callback_data=PLAYER_BACKS_CB
)
