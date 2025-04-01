from collections import Counter

from cache.cache_types import PlayersIds, GameCache
from utils.pretty_text import make_build


def get_the_most_frequently_encountered_id(ids: PlayersIds):
    if not ids:
        return None
    if len(set(ids)) == 1:
        return ids[0]
    most_common = Counter(ids).most_common()
    if most_common[0][1] == most_common[1][1]:
        return None
    return most_common[0][0]


def save_notification_message(
    game_data: GameCache,
    processed_user_id: int,
    message: str,
    current_user_id: int | None,
):

    if (
        current_user_id is None
        or processed_user_id != current_user_id
    ):
        game_data["messages_after_night"].append(
            [processed_user_id, message]
        )
