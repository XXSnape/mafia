import enum
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
    angels_of_death: PlayersIds
    angels_died: PlayersIds
    to_delete: ChatsAndMessagesIds
    vote_for: PlayersIds
    protected: PlayersIds
    self_protected: PlayersIds
    have_alibi: PlayersIds
    prime_ministers: PlayersIds
    instigators: PlayersIds
    missed: PlayersIds

    # wait_for: list[int]
    two_voices: PlayersIds
    last_treated: int
    last_arrested: int
    last_forgiven: int
    last_self_protected: int
    number_of_night: int


from enum import StrEnum
from typing import NamedTuple

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
    "instigators",
    "civilians",
    "prime_ministers",
    "angels_of_death",
    "angels_died",
]

LastProcessedLiteral = Literal[
    "last_treated",
    "last_arrested",
    "last_forgiven",
    "last_self_protected",
]

ListToProcessLiteral = Literal[
    "self_protected",
    "recovered",
    "have_alibi",
    "cant_vote",
    "missed",
]


class Groupings(StrEnum):
    criminals = "criminals"
    civilians = "civilians"
    masochists = "masochists"
    suicide_bombers = "suicide_bombers"
    other = "other"


class Role(NamedTuple):
    role: str
    roles_key: RolesKeysLiteral
    last_interactive: LastProcessedLiteral | None
    photo: str
    grouping: str
    purpose: str


class Roles(enum.Enum):
    mafia = Role(
        role="Мафия",
        roles_key="mafias",
        last_interactive=None,
        photo="https://i.pinimg.com/736x/a1/10/db/a110db3eaba78bf6423bcea68f330a64.jpg",
        grouping=Groupings.criminals,
        purpose="Тебе нужно уничтожить всех горожан.",
    )
    doctor = Role(
        role="Доктор",
        roles_key="doctors",
        last_interactive="last_treated",
        photo="https://gipermed.ru/upload/iblock/4bf/4bfa55f59ceb538bd2c8c437e8f71e5a.jpg",
        grouping=Groupings.civilians,
        purpose="Тебе нужно стараться лечить тех, кому нужна помощь.",
    )
    angel_of_death = Role(
        role="Ангел смерти",
        roles_key="angels_of_death",
        last_interactive=None,
        photo="https://avatars.mds.yandex.net/get-entity_search/10844899/935958285/S600xU_2x",
        purpose="Если ты умрешь на голосовании, сможешь ночью забрать кого-нибудь с собой",
        grouping=Groupings.civilians,
    )
    policeman = Role(
        role="Комиссар",
        roles_key="policeman",
        last_interactive=None,
        photo="https://avatars.mds.yandex.net/get-kinopoisk-image/"
        "1777765/59ba5e74-7a28-47b2-944a-2788dcd7ebaa/1920x",
        grouping=Groupings.civilians,
        purpose="Тебе нужно вычислить мафию.",
    )
    # policeman = "Комиссар"
    prosecutor = Role(
        role="Прокурор",
        roles_key="prosecutors",
        last_interactive="last_arrested",
        photo="https://avatars.mds.yandex.net/i?"
        "id=b5115d431dafc24be07a55a8b6343540_l-5205087-images-thumbs&n=13",
        grouping=Groupings.civilians,
        purpose="Тебе нельзя допустить, чтобы днем мафия могла говорить.",
    )
    # prosecutor = "Прокурор"
    lawyer = Role(
        role="Адвокат",
        roles_key="lawyers",
        last_interactive="last_forgiven",
        photo="https://avatars.mds.yandex.net/get-altay/"
        "5579175/2a0000017e0aa51c3c1fd887206b0156ee34/XXL_height",
        grouping=Groupings.civilians,
        purpose="Тебе нужно защитить мирных жителей от своих же на голосовании.",
    )
    # lawyer = "Адвокат"
    civilian = Role(
        role="Мирный житель",
        roles_key="civilians",
        last_interactive=None,
        photo="https://cdn.culture.ru/c/820179.jpg",
        grouping=Groupings.civilians,
        purpose="Тебе нужно вычислить мафию на голосовании.",
    )
    # civilian = "Мирный житель"
    masochist = Role(
        role="Мазохист",
        roles_key="masochists",
        last_interactive=None,
        photo="https://i.pinimg.com/736x/14/a5/f5/14a5f5eb5dbd73c4707f24d436d80c0b.jpg",
        grouping=Groupings.masochists,
        purpose="Тебе нужно умереть на дневном голосовании.",
    )
    # masochist = "Мазохист"
    lucky_gay = Role(
        role="Везунчик",
        roles_key="lucky_guys",
        last_interactive=None,
        photo="https://avatars.mds.yandex.net/get-mpic/5031100/img_id5520953584482126492.jpeg/orig",
        grouping=Groupings.civilians,
        purpose="Возможно тебе повезет и ты останешься жив после покушения.",
    )
    # lucky_gay = "Везунчик"
    suicide_bomber = Role(
        role="Ночной смертник",
        roles_key="suicide_bombers",
        last_interactive=None,
        photo="https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
        "size=1280x1280&quality=96&"
        "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
        "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album",
        grouping=Groupings.suicide_bombers,
        purpose="Тебе нужно умереть ночью.",
    )
    # suicide_bomber = "Ночной смертник"
    bodyguard = Role(
        role="Телохранитель",
        roles_key="bodyguards",
        last_interactive="last_self_protected",
        photo="https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
        "size=1280x1280&quality=96&"
        "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
        "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album",
        grouping=Groupings.civilians,
        purpose="Тебе нужно защитить собой лучших специалистов",
    )
    prime_minister = Role(
        role="Премьер-министр",
        roles_key="prime_ministers",
        last_interactive=None,
        photo="https://avatars.mds.yandex.net/i?id=fb2e5e825d183d5344d93bc5636bc4c4_l-5084109-images-thumbs&n=13",
        grouping=Groupings.civilians,
        purpose="Твой голос стоит как 2!",
    )
    # bodyguard = "Телохранитель"
    # prime_minister = "Премьер-министр"
    instigator = Role(
        role="Подстрекатель",
        roles_key="instigators",
        last_interactive=None,
        photo="https://avatars.dzeninfra.ru/get-zen_doc/3469057/"
        "pub_620655d2a7947c53d6c601a2_620671b4b495be46b12c0a0c/scale_1200",
        grouping=Groupings.other,
        purpose="Твоя жертва всегда ошибется при выборе на голосовании.",
    )
