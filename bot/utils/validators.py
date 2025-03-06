from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cache.cache_types import GameCache, PlayersIds


def are_not_sleeping_killers(game_data: "GameCache") -> "PlayersIds":
    if game_data["number_of_night"] % 2 != 0:
        return game_data["killers"]
    return []


def angel_died_2_nights_ago_or_earlier(game_data: "GameCache"):
    current_number = game_data["number_of_night"]
    angels = []
    for angel_id in game_data["angels_died"]:
        if (
            current_number
            - game_data["players"][str(angel_id)][
                "number_died_at_night"
            ]
        ) in (1, 2):
            angels.append(angel_id)
    return angels
