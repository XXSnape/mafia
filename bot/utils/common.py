from collections import Counter
from contextlib import suppress
from functools import partial
from typing import Literal

from aiogram.types import CallbackQuery
from cache.cache_types import GameCache, PlayersIds


def get_the_most_frequently_encountered_id(
    ids: PlayersIds, counterweight: int | None = None
):
    if not ids:
        return None
    if len(set(ids)) == 1:
        if counterweight and counterweight >= len(ids):
            return None
        return ids[0]
    most_common = Counter(ids).most_common()
    if most_common[0][1] == most_common[1][1]:
        return None
    if counterweight and counterweight >= most_common[0][1]:
        return None
    return most_common[0][0]


def get_criminals_ids(game_data: GameCache) -> PlayersIds:
    from mafia.roles import Forger, Lucifer, Mafia, Traitor

    return (
        game_data.get(Mafia.roles_key, [])
        + game_data.get(Traitor.roles_key, [])
        + game_data.get(Forger.roles_key, [])
        + game_data.get(Lucifer.roles_key, [])
    )


def add_message_to_delete(
    game_data: GameCache, chat_id: int, message_id: int
):
    game_data["to_delete"].append([chat_id, message_id])


def remove_from_expected(
    callback: CallbackQuery,
    game_data: GameCache,
    key: Literal[
        "waiting_for_action_at_night",
        "waiting_for_action_at_day",
    ],
    need_to_remove_from_expected: bool = True,
):
    if need_to_remove_from_expected:
        with suppress(ValueError):
            game_data[key].remove(callback.from_user.id)
    with suppress(ValueError):
        game_data["to_delete"].remove(
            [callback.from_user.id, callback.message.message_id]
        )


remove_from_expected_at_night = partial(
    remove_from_expected, key="waiting_for_action_at_night"
)
remove_from_expected_at_day = partial(
    remove_from_expected, key="waiting_for_action_at_day"
)
