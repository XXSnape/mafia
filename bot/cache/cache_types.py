from dataclasses import dataclass
from typing import NotRequired, TypeAlias, TypedDict, Literal


@dataclass
class ExtraCache:
    key: str
    is_cleared: bool = True
    data_type: type = list


Url: TypeAlias = str
PlayersIds: TypeAlias = list[int]
UserIdStr: TypeAlias = str
RoleName: TypeAlias = str
UserIdInt: TypeAlias = int
Message: TypeAlias = str
RolesLiteral = Literal[
    "don",
    "doctor",
    "policeman",
    "traitor",
    "killer",
    "werewolf",
    "forger",
    "hacker",
    "sleeper",
    "agent",
    "journalist",
    "punisher",
    "analyst",
    "suicide_bomber",
    "instigator",
    "prime_minister",
    "bodyguard",
    "masochist",
    "lawyer",
    "angel_of_death",
    "prosecutor",
    "civilian",
    "lucky_gay",
    "mafia",
    "nurse",
    "general",
]

Money: TypeAlias = int
Achievements: TypeAlias = list[str]
Poisoned: TypeAlias = list[list[int] | int]


class OrderOfRolesCache(TypedDict, total=True):
    attacking: list[RolesLiteral]
    other: list[RolesLiteral]
    selected: list[RolesLiteral]


class PollBannedRolesCache(TypedDict, total=False):
    available_roles: list[str]
    number: int
    max_number: int
    banned_roles: list[str]
    poll_id: int
    last_msg_id: int


class UserGameCache(TypedDict, total=False):
    full_name: str
    url: Url
    role: NotRequired[RoleName]
    pretty_role: NotRequired[str]
    initial_role: str
    enum_name: RolesLiteral
    roles_key: str
    number_died_at_night: int
    user_id: int
    money: Money
    is_winner: bool
    achievements: Achievements


UsersInGame: TypeAlias = dict[UserIdStr, UserGameCache]
LivePlayersIds: TypeAlias = PlayersIds
ChatsAndMessagesIds: TypeAlias = list[list[int]]
MessagesAfterNight: TypeAlias = list[list[UserIdInt | Message]]


class InteractionData(TypedDict):
    sufferers: PlayersIds
    interacting: PlayersIds


TrackingData: TypeAlias = dict[UserIdStr, InteractionData]
NumberOfNight: TypeAlias = int

LastInteraction: TypeAlias = dict[UserIdStr, list[NumberOfNight]]
DisclosedRoles = list[list[UserIdStr, RoleName]]
VotedFor: TypeAlias = list[list[UserIdInt]]


class UserCache(TypedDict):
    game_chat: int


class GameCache(TypedDict, total=False):
    owner: int
    game_chat: int
    messages_after_night: MessagesAfterNight
    disclosed_roles: DisclosedRoles
    pros: PlayersIds
    cons: PlayersIds
    players_ids: LivePlayersIds
    players: UsersInGame
    tracking: TrackingData
    text_about_checks: str
    to_delete: ChatsAndMessagesIds
    vote_for: VotedFor
    winners: PlayersIds
    losers: PlayersIds
    number_of_night: NumberOfNight
