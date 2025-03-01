from enum import StrEnum
from typing import TypedDict, TypeAlias, NotRequired, Literal


class Roles:
    mafia = "Мафия"
    doctor = "Доктор"
    policeman = "Комиссар"
    civilian = "Мирный житель"


class UserGameCache(TypedDict):
    full_name: str
    url: str
    role: NotRequired[str]


UsersInGame: TypeAlias = dict[str, UserGameCache]

LivePlayersIds: TypeAlias = list[int]


class UserCache(TypedDict):
    game_chat: int


class GameCache(TypedDict):
    owner: int
    game_chat: int
    players_ids: LivePlayersIds
    players: UsersInGame
    mafias: list[int]
    doctors: list[int]
    policeman: list[int]
    civilians: list[int]
    died: list[int]
    recovered: list[int]
    to_delete: list[int]
    # wait_for: list[int]
    last_treated: int
    number_of_night: int


RolesKeysLiteral = Literal["mafias", "doctors", "policeman"]
