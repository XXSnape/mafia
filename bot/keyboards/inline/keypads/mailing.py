from collections.abc import Iterable
from operator import attrgetter

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from cache.cache_types import GameCache, UserIdInt, UsersInGame
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import BACK_BTN
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import (
    POISONER_POISONS_CB,
    POLICEMAN_CHECKS_CB,
    POLICEMAN_KILLS_CB,
    WEREWOLF_TO_DOCTOR_CB,
    WEREWOLF_TO_MAFIA_CB,
    WEREWOLF_TO_POLICEMAN_CB,
)
from utils.common import get_criminals_ids


def send_transformation_kb(game_data: GameCache):
    from mafia.roles import (
        Doctor,
        MafiaAlias,
        Policeman,
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
    criminals_ids = get_criminals_ids(game_data)
    if len(criminals_ids) + 1 < (
        len(game_data["live_players_ids"]) - (len(criminals_ids) + 1)
    ):
        buttons.append(
            InlineKeyboardButton(
                text=MafiaAlias.role,
                callback_data=WEREWOLF_TO_MAFIA_CB,
            )
        )
    return generate_inline_kb(data_with_buttons=buttons)


def send_selection_to_players_kb(
    players_ids: list[UserIdInt],
    players: UsersInGame,
    extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    exclude: Iterable[UserIdInt] | UserIdInt = (),
    user_index_cb: type[CallbackData] = UserActionIndexCbData,
):
    if isinstance(exclude, UserIdInt):
        exclude = [exclude]
    buttons = [
        InlineKeyboardButton(
            text=players[str(player_id)]["full_name"],
            callback_data=user_index_cb(user_index=index).pack(),
        )
        for index, player_id in enumerate(players_ids)
        if player_id not in exclude
    ]
    buttons.sort(key=attrgetter("text"))
    buttons += extra_buttons
    return generate_inline_kb(data_with_buttons=buttons)


def selection_to_warden_kb(game_data: GameCache, user_id: UserIdInt):
    checked = game_data["checked_for_the_same_groups"]
    buttons = []
    for player_id in game_data["live_players_ids"]:
        if player_id == user_id:
            continue
        text = game_data["players"][str(player_id)]["full_name"]
        if checked and player_id == checked[0]:
            text = "✅" + text
        buttons.append(
            InlineKeyboardButton(
                text=text, callback_data=str(player_id)
            )
        )
    return generate_inline_kb(data_with_buttons=buttons)


def kill_or_poison_kb(game_data: GameCache):
    poisoned = game_data["poisoned"]
    buttons = []
    if (
        not poisoned
        or len(poisoned[0]) < len(game_data["live_players_ids"]) - 1
    ):
        buttons.append(
            InlineKeyboardButton(
                text="Отравить🤢", callback_data=POISONER_POISONS_CB
            ),
        )
    if poisoned and poisoned[0]:
        buttons.append(
            InlineKeyboardButton(
                text="Убить☠️", callback_data=POLICEMAN_KILLS_CB
            )
        )
    return generate_inline_kb(data_with_buttons=buttons)


def kill_or_check_on_policeman(game_data: GameCache):
    buttons = [
        InlineKeyboardButton(
            text="Проверить🔍",
            callback_data=POLICEMAN_CHECKS_CB,
        ),
    ]
    if (
        game_data["number_of_night"] > 1
        and game_data["settings"]["can_marshal_kill"]
    ):
        buttons.append(
            InlineKeyboardButton(
                text="Стрелять🔫",
                callback_data=POLICEMAN_KILLS_CB,
            ),
        )
    return generate_inline_kb(data_with_buttons=buttons)


def choose_fake_role_kb(game_data: GameCache):
    from general.collection_of_roles import get_data_with_roles
    from mafia.roles import Policeman

    policeman = (
        Policeman.role_id,
        Policeman.alias.role_id,
    )
    all_roles = get_data_with_roles()
    current_roles = set()
    if game_data["settings"]["show_roles_after_death"]:
        users = game_data["live_players_ids"]
    else:
        users = game_data["players"].keys()
    for user_id in users:
        user_data = game_data["players"][str(user_id)]
        if user_data["role_id"] not in policeman:
            current_roles.add(
                (
                    all_roles[user_data["role_id"]].role,
                    user_data["role_id"],
                )
            )

    buttons = [
        InlineKeyboardButton(text=role[0], callback_data=role[1])
        for role in current_roles
    ]
    buttons.sort(key=attrgetter("text"))
    buttons.append(BACK_BTN)
    return generate_inline_kb(data_with_buttons=buttons)
