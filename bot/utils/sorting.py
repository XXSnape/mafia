from collections.abc import MutableSequence


from cache.cache_types import (
    RolesLiteral,
    UserIdStr,
    UserIdInt,
    UsersInGame,
)


def sorting_roles_by_name(role_key: RolesLiteral):
    from general.collection_of_roles import get_data_with_roles

    return get_data_with_roles(role_key).role


def sorting_by_rate(
    role_and_winners_with_money: tuple[RolesLiteral, list[int]],
):
    return role_and_winners_with_money[1][1]


def sorting_by_money(players: UsersInGame):
    def wrapper(user_id: UserIdStr | UserIdInt):
        return -players[str(user_id)]["money"]

    return wrapper


def sorting_by_number(players: UsersInGame):
    def wrapper(user_id: UserIdStr | UserIdInt):
        return players[str(user_id)].get("number", 0)

    return wrapper


def sorting_by_voting(voting_data: MutableSequence[str, list[str]]):
    return len(voting_data[1])
