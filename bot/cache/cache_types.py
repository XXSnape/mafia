from typing import (
    TypedDict,
    TypeAlias,
    NotRequired,
    Literal,
)


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
    have_alibi: PlayersIds
    prime_ministers: PlayersIds

    # wait_for: list[int]
    two_voices: PlayersIds
    last_treated: int
    last_arrested: int
    last_forgiven: int
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
LastProcessedLiteral = Literal[
    "last_treated",
    "last_arrested",
    "last_forgiven",
    "last_self_protected",
]
ListToProcessLiteral = Literal[
    "self_protected", "recovered", "have_alibi", "cant_vote"
]
