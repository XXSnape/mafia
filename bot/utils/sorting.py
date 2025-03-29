from cache.cache_types import RolesLiteral, UserIdStr, GameCache
from general.collection_of_roles import get_data_with_roles


def sort_roles_by_name(role_key: RolesLiteral):
    return get_data_with_roles(role_key).role


def sorting_by_rate(
    role_and_winners_with_money: tuple[RolesLiteral, list[int]],
):
    return role_and_winners_with_money[1][1]


def sorting_by_money(game_data: GameCache):
    def wrapper(user_id: UserIdStr):
        return game_data["players"][user_id]["money"]
    return wrapper
