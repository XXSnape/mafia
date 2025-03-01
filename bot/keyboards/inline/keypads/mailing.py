from collections.abc import Iterable

from aiogram.types import InlineKeyboardButton

from cache.cache_types import UsersInGame
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.callback_factory.user_index import (
    UserIndexCbData,
)


def send_selection_to_players_kb(
    players_ids: list[int],
    players: UsersInGame,
    exclude: Iterable[int] | int = (),
):
    if isinstance(exclude, int):
        exclude = [exclude]
    buttons = [
        InlineKeyboardButton(
            text=players[str(player_id)]["full_name"],
            callback_data=UserIndexCbData(user_index=index).pack(),
        )
        for index, player_id in enumerate(players_ids)
        if player_id not in exclude
    ]
    return generate_inline_kb(data_with_buttons=buttons)
