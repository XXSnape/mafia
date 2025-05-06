from typing import Literal, TypeAlias, TypedDict

PlayersIds: TypeAlias = list[int | str]
UserIdStr: TypeAlias = str
UserIdInt: TypeAlias = int
NumberOfNight: TypeAlias = int
LastInteraction: TypeAlias = dict[UserIdStr, list[NumberOfNight]]
UserAndMoney: TypeAlias = list[int]
UsersMoney: TypeAlias = list[UserAndMoney]
UsersInGame: TypeAlias = dict[UserIdStr, "UserGameCache"]
StagesOfGameLiteral = Literal[
    "time_for_night",
    "time_for_day",
    "time_for_voting",
    "time_for_confirmation",
]
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
    "warden",
    "poisoner",
]
RolesAndUsersMoney: TypeAlias = dict[RolesLiteral, UsersMoney]
RoleAndUserMoney: TypeAlias = dict[RolesLiteral, UserAndMoney]


class OrderOfRolesCache(TypedDict, total=True):
    attacking: list[RolesLiteral]
    other: list[RolesLiteral]
    selected: list[RolesLiteral]
    criminal_every_3: bool


class PollBannedRolesCache(TypedDict, total=False):
    banned_roles_ids: list[RolesLiteral]


class DifferentSettingsCache(TypedDict):
    time_for_night: int
    time_for_day: int
    time_for_voting: int
    time_for_confirmation: int
    show_roles_after_death: bool
    show_peaceful_allies: bool
    show_killers: bool
    show_information_about_guests_at_night: bool
    show_usernames_during_voting: bool
    show_usernames_after_confirmation: bool
    can_kill_teammates: bool
    can_marshal_kill: bool
    mafia_every_3: bool
    allow_betting: bool
    speed_up_nights_and_voting: bool


class AllSettingsCache(TypedDict, total=False):
    poll_banned_roles: PollBannedRolesCache
    order_of_roles: OrderOfRolesCache
    different_settings: DifferentSettingsCache


class PersonalSettingsCache(TypedDict, total=False):
    settings: AllSettingsCache


class UserGameCache(TypedDict, total=False):
    full_name: str
    url: str
    number: int
    pretty_role: str
    initial_role: str
    role_id: RolesLiteral
    initial_role_id: RolesLiteral
    roles_key: str
    number_died_at_night: int
    money: int
    achievements: list[list[str | UserIdInt]]


class InteractionData(TypedDict):
    sufferers: PlayersIds
    interacting: PlayersIds


class GameSettingsCache(DifferentSettingsCache, total=False):
    creator_user_id: int
    creator_full_name: str
    order_of_roles: list[RolesLiteral]
    banned_roles: list[RolesLiteral]


class UserCache(TypedDict, total=False):
    game_chat: int
    message_with_offer_id: int
    coveted_role: RolesLiteral
    balance: int


class GameCache(TypedDict, total=False):
    settings: GameSettingsCache
    bids: RolesAndUsersMoney
    game_chat: int
    start_message_id: int
    waiting_for_action_at_night: PlayersIds
    waiting_for_action_at_day: PlayersIds
    messages_after_night: list[list[UserIdInt | str]]
    disclosed_roles: PlayersIds
    forged_roles: list[UserIdInt | RolesLiteral]
    checked_for_the_same_groups: PlayersIds
    mafias_are_shown: PlayersIds
    deceived: PlayersIds
    poisoned: list[list[UserIdInt] | bool]
    pros: PlayersIds
    cons: PlayersIds
    refused_to_vote: PlayersIds
    live_players_ids: PlayersIds
    players: UsersInGame
    tracking: dict[UserIdStr, InteractionData]
    text_about_checks: str
    text_about_checked_for_the_same_groups: str
    to_delete: list[list[int]]
    vote_for: list[PlayersIds]
    winners: PlayersIds
    losers: PlayersIds
    number_of_night: NumberOfNight
    start_of_registration: int
    end_of_registration: int
    angels_died: PlayersIds
    cant_vote: PlayersIds
    cant_talk: PlayersIds
    wish_to_leave_game: PlayersIds
