from typing import TypedDict, TypeAlias


class UserGameCache(TypedDict):
    full_name: str


UsersInGame: TypeAlias = dict[str, UserGameCache]


class UserCache(TypedDict):
    game_chat: int


class GameCache(TypedDict, total=False):
    owner: int
    players_ids: list[int]
    players: dict[str, UserGameCache]
    mafias: list[int]
    doctors: list[int]
    policeman: list[int]
    civilians: list[int]
    died: list[int]
    mafia_poll_delete: int
    number_of_night: int
