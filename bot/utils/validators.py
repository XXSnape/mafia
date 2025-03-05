from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cache.cache_types import GameCache


def is_not_sleeping_killer(game_data: "GameCache") -> bool:
    return game_data["number_of_night"] % 2 != 0
