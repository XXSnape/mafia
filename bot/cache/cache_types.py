from enum import StrEnum
from typing import (
    TypedDict,
    TypeAlias,
    NotRequired,
    Literal,
    Iterable,
)


class Groupings(StrEnum):
    criminals = "criminals"
    civilians = "civilians"
    masochists = "masochists"
    suicide_bombers = "suicide_bombers"


class Roles:
    mafia = "Мафия"
    doctor = "Доктор"
    policeman = "Комиссар"
    prosecutor = "Прокурор"
    lawyer = "Адвокат"
    civilian = "Мирный житель"
    masochist = "Мазохист"
    lucky_gay = "Везунчик"
    suicide_bomber = "Ночной смертник"
    bodyguard = "Телохранитель"


class UserGameCache(TypedDict):
    full_name: str
    url: str
    role: NotRequired[str]
    pretty_role: NotRequired[str]


UsersInGame: TypeAlias = dict[str, UserGameCache]

PlayersIds: TypeAlias = list[int]
LivePlayersIds: TypeAlias = PlayersIds
ChatsAndMessagesIds: TypeAlias = list[list[int]]


class UserCache(TypedDict):
    game_chat: int


class GameCache(TypedDict, total=True):
    owner: int
    game_chat: int
    pros: PlayersIds
    cons: PlayersIds
    players_ids: LivePlayersIds
    players: UsersInGame

    prosecutors: PlayersIds
    mafias: PlayersIds
    doctors: PlayersIds
    policeman: PlayersIds
    lucky_guys: PlayersIds
    bodyguards: PlayersIds
    civilians: PlayersIds
    lawyers: PlayersIds
    died: PlayersIds
    masochists: PlayersIds
    suicide_bombers: PlayersIds
    winners: PlayersIds
    losers: PlayersIds
    cant_vote: PlayersIds
    recovered: PlayersIds
    to_delete: ChatsAndMessagesIds
    vote_for: PlayersIds
    protected: PlayersIds
    self_protected: PlayersIds

    # wait_for: list[int]
    last_treated: int
    last_arrested: int
    last_protected: int
    last_self_protected: int
    number_of_night: int


RolesKeysLiteral = Literal[
    "mafias",
    "doctors",
    "policeman",
    "prosecutors",
    "lawyers",
    "masochists",
    "lucky_guys",
    "suicide_bombers",
    "bodyguards",
]
