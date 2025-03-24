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
    banned_roles_keys: list[RolesLiteral]


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


class OwnerCache(TypedDict):
    user_id: int
    full_name: str
    order_of_roles: list[RolesLiteral]
    banned_roles: list[RolesLiteral]


UserAndMoney = list[int]
UsersMoney = list[UserAndMoney]

RolesAndUsersMoney = dict[RolesLiteral, UsersMoney]


class UserCache(TypedDict, total=False):
    game_chat: int
    message_with_offer_id: int
    coveted_role: RolesLiteral


class BettingResultsCache:
    winners: UserAndMoney
    loses: UserAndMoney


class GameCache(TypedDict, total=False):
    owner: OwnerCache
    bids: RolesAndUsersMoney
    betting_results: dict[RolesLiteral, BettingResultsCache]
    game_chat: int
    start_message_id: int
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
    start_of_registration: int
    end_of_registration: int
