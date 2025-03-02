from enum import StrEnum
from typing import TypedDict, TypeAlias, NotRequired, Literal


class Groupings(StrEnum):
    criminals = "criminals"
    civilians = "civilians"


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

PlayersIds: TypeAlias = list[int]
LivePlayersIds: TypeAlias = PlayersIds


class UserCache(TypedDict):
    game_chat: int


class GameCache(TypedDict, total=True):
    owner: int
    game_chat: int
    pros: PlayersIds
    cons: PlayersIds
    players_ids: LivePlayersIds
    players: UsersInGame
    mafias: PlayersIds
    doctors: PlayersIds
    policeman: PlayersIds
    civilians: PlayersIds
    died: PlayersIds
    recovered: PlayersIds
    to_delete: PlayersIds
    vote_for: PlayersIds
    # wait_for: list[int]
    last_treated: int
    number_of_night: int


RolesKeysLiteral = Literal["mafias", "doctors", "policeman"]
