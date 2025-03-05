import enum
from dataclasses import dataclass
from typing import (
    TypedDict,
    TypeAlias,
    NotRequired,
    Literal,
)

from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardButton

from keyboards.inline.cb.cb_text import DRAW_CB
from states.states import UserFsm

Url: TypeAlias = str


class UserGameCache(TypedDict):
    full_name: str
    url: Url
    role: NotRequired[str]
    pretty_role: NotRequired[str]


UserIdStr: TypeAlias = str
UsersInGame: TypeAlias = dict[UserIdStr, UserGameCache]

PlayersIds: TypeAlias = list[int]
LivePlayersIds: TypeAlias = PlayersIds
ChatsAndMessagesIds: TypeAlias = list[list[int]]


class InteractionData(TypedDict):
    sufferers: PlayersIds
    interacting: PlayersIds


TrackingData: TypeAlias = dict[UserIdStr, InteractionData]


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
    masochists: PlayersIds
    suicide_bombers: PlayersIds
    winners: PlayersIds
    losers: PlayersIds
    angels_of_death: PlayersIds
    to_delete: ChatsAndMessagesIds
    vote_for: PlayersIds
    prime_ministers: PlayersIds
    instigators: PlayersIds
    agents: PlayersIds

    tracked: PlayersIds
    angels_died: PlayersIds
    killed_by_mafia: PlayersIds
    killed_by_don: PlayersIds
    killed_by_policeman: PlayersIds
    killed_by_angel_of_death: PlayersIds
    treated_by_doctor: PlayersIds
    treated_by_bodyguard: PlayersIds
    voted_by_prime: PlayersIds
    self_protected: PlayersIds
    have_alibi: PlayersIds
    cant_vote: PlayersIds
    missed: PlayersIds
    analysts: PlayersIds
    predicted: PlayersIds
    punishers: PlayersIds
    journalists: PlayersIds
    talked: PlayersIds
    tracking: TrackingData

    # wait_for: list[int]
    two_voices: PlayersIds
    last_tracked_by_agent: PlayersIds
    last_treated_by_doctor: PlayersIds
    last_arrested_by_prosecutor: PlayersIds
    last_forgiven_by_lawyer: PlayersIds
    last_self_protected_by_bodyguard: PlayersIds

    number_of_night: int


from enum import StrEnum

RolesKeysLiteral = Literal[
    "journalists",
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
    "analysts",
    "punishers",
    "agents",
]

LastProcessedLiteral = Literal[
    "last_treated_by_doctor",
    "last_arrested_by_prosecutor",
    "last_forgiven_by_lawyer",
    "last_self_protected_by_bodyguard",
    "last_tracked_by_agent",
]


class Groupings(StrEnum):
    criminals = "criminals"
    civilians = "civilians"
    masochists = "masochists"
    suicide_bombers = "suicide_bombers"
    other = "other"


ListToProcessLiteral = Literal[
    "angels_died",
    "killed_by_mafia",
    "killed_by_don",
    "talked",
    "killed_by_policeman",
    "killed_by_angel_of_death",
    "treated_by_doctor",
    "treated_by_bodyguard",
    "voted_by_prime",
    "self_protected",
    "have_alibi",
    "cant_vote",
    "missed",
    "predicted",
    "tracking",
    "tracked",
]


@dataclass
class ExtraCache:
    key: ListToProcessLiteral
    is_cleared: bool = True
    data_type: type = list


@dataclass
class Role:
    role: str
    roles_key: RolesKeysLiteral
    processed_users_key: ListToProcessLiteral | None
    photo: str
    grouping: str
    purpose: str
    is_self_selecting: bool = False
    mail_message: str | None = None
    message_to_user_after_action: str | None = None
    message_to_group_after_action: str | None = None
    last_interactive_key: LastProcessedLiteral | None = None
    is_mass_mailing_list: bool = False
    extra_data: list[ExtraCache] | None = None
    state_for_waiting_for_action: State | None = None
    for_notifications: ListToProcessLiteral | None = None
    extra_buttons_for_actions_at_night: tuple[
        InlineKeyboardButton, ...
    ] = ()
    can_kill_at_night_and_survive: bool = False


class Roles(enum.Enum):
    mafia = Role(
        role="Мафия",
        roles_key="mafias",
        processed_users_key="killed_by_mafia",
        photo="https://i.pinimg.com/736x/a1/10/db/a110db3eaba78bf6423bcea68f330a64.jpg",
        grouping=Groupings.criminals,
        purpose="Тебе нужно уничтожить всех горожан.",
        message_to_group_after_action="Мафия выбрала жертву!",
        message_to_user_after_action="Ты выбрал убить {url}",
        extra_data=[ExtraCache("killed_by_don")],
        mail_message="Кого убить этой ночью?",
        is_mass_mailing_list=True,
        state_for_waiting_for_action=UserFsm.MAFIA_ATTACKS,
        can_kill_at_night_and_survive=True,
    )

    policeman = Role(
        role="Комиссар",
        roles_key="policeman",
        processed_users_key="killed_by_policeman",
        photo="https://avatars.mds.yandex.net/get-kinopoisk-image/"
        "1777765/59ba5e74-7a28-47b2-944a-2788dcd7ebaa/1920x",
        grouping=Groupings.civilians,
        purpose="Тебе нужно вычислить мафию.",
        message_to_group_after_action="Работает местная полиция! Всем жителям приказано сидеть дома!",
        message_to_user_after_action="Ты выбрал узнать роль {url}",
        mail_message="Кого проверить этой ночью?",
        state_for_waiting_for_action=UserFsm.POLICEMAN_CHECKS,
        can_kill_at_night_and_survive=True,
    )
    agent = Role(
        role="Агент 008",
        processed_users_key="tracked",
        last_interactive_key="last_tracked_by_agent",
        roles_key="agents",
        photo="https://avatars.mds.yandex.net/i?id="
        "7b6e30fff5c795d560c07b69e7e9542f044fcaf9e04d4a31-5845211-images-thumbs&n=13",
        grouping=Groupings.civilians,
        purpose="Ты можешь следить за кем-нибудь ночью",
        message_to_group_after_action="Спецслужбы выходят на разведу",
        message_to_user_after_action="Ты выбрал следить за {url}",
        mail_message="За кем следить этой ночью?",
        state_for_waiting_for_action=UserFsm.AGENT_WATCHES,
        extra_data=[
            ExtraCache(key="tracking", data_type=dict),
        ],
    )
    journalist = Role(
        role="Журналист",
        processed_users_key="talked",
        roles_key="journalists",
        photo="https://pics.rbc.ru/v2_companies_s3/resized/"
        "960xH/media/company_press_release_image/"
        "022eef78-63a5-4a2b-bb88-e4dcae639e34.jpg",
        grouping=Groupings.civilians,
        purpose="Ты можешь приходить к местным жителям и узнавать, что они видели",
        message_to_group_after_action="Что случилось? Отчаянные СМИ спешат выяснить правду!",
        message_to_user_after_action="Ты выбрал взять интервью у {url}",
        mail_message="У кого взять интервью этой ночью?",
        state_for_waiting_for_action=UserFsm.JOURNALIST_TAKES_INTERVIEW,
        extra_data=[
            ExtraCache(key="tracking", data_type=dict),
        ],
    )
    doctor = Role(
        role="Доктор",
        roles_key="doctors",
        processed_users_key="treated_by_doctor",
        last_interactive_key="last_treated_by_doctor",
        photo="https://gipermed.ru/upload/iblock/4bf/4bfa55f59ceb538bd2c8c437e8f71e5a.jpg",
        grouping=Groupings.civilians,
        purpose="Тебе нужно стараться лечить тех, кому нужна помощь.",
        message_to_group_after_action="Доктор спешит кому-то на помощь!",
        message_to_user_after_action="Ты выбрал вылечить {url}",
        mail_message="Кого вылечить этой ночью?",
        is_self_selecting=True,
        state_for_waiting_for_action=UserFsm.DOCTOR_TREATS,
    )

    punisher = Role(
        role="Каратель",
        processed_users_key=None,
        roles_key="punishers",
        photo="https://lastfm.freetls.fastly.net/i/u/ar0/d04cdfdf3f65412bc1e7870ec6599ed7.png",
        grouping=Groupings.civilians,
        purpose="Спровоцируй мафию и забери её с собой!",
    )

    analyst = Role(
        role="Политический аналитик",
        processed_users_key="predicted",
        roles_key="analysts",
        photo="https://habrastorage.org/files/2e3/371/6a2/2e33716a2bb74f8eb67378334960ebb5.png",
        grouping=Groupings.civilians,
        purpose="Тебе нужно на основе ранее полученных данных предсказать, кого повесят на дневном голосовании",
        is_self_selecting=True,
        mail_message="Кого повесят сегодня днём?",
        message_to_group_after_action="Составляется прогноз на завтрашний день",
        message_to_user_after_action="Ты предположил, что повесят {url}",
        extra_buttons_for_actions_at_night=(
            InlineKeyboardButton(
                text="У жителей не хватит политической воли",
                callback_data=DRAW_CB,
            ),
        ),
        state_for_waiting_for_action=UserFsm.ANALYST_ASSUMES,
    )
    suicide_bomber = Role(
        role="Ночной смертник",
        roles_key="suicide_bombers",
        processed_users_key=None,
        photo="https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
        "size=1280x1280&quality=96&"
        "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
        "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album",
        grouping=Groupings.suicide_bombers,
        purpose="Тебе нужно умереть ночью.",
    )
    instigator = Role(
        role="Подстрекатель",
        roles_key="instigators",
        processed_users_key="missed",
        photo="https://avatars.dzeninfra.ru/get-zen_doc/3469057/"
        "pub_620655d2a7947c53d6c601a2_620671b4b495be46b12c0a0c/scale_1200",
        grouping=Groupings.other,
        purpose="Твоя жертва всегда ошибется при выборе на голосовании.",
        message_to_group_after_action="Кажется, кто-то становится жертвой психологического насилия!",
        message_to_user_after_action="Ты выбрал прополоскать мозги {url}",
        mail_message="Кого надоумить на неправильный выбор?",
        state_for_waiting_for_action=UserFsm.INSTIGATOR_LYING,
    )
    prime_minister = Role(
        role="Премьер-министр",
        roles_key="prime_ministers",
        processed_users_key="voted_by_prime",
        photo="https://avatars.mds.yandex.net/i?id=fb2e5e825d183d5344d93bc5636bc4c4_l-5084109-images-thumbs&n=13",
        grouping=Groupings.civilians,
        purpose="Твой голос стоит как 2!",
    )
    bodyguard = Role(
        role="Телохранитель",
        roles_key="bodyguards",
        processed_users_key="treated_by_bodyguard",
        last_interactive_key="last_self_protected_by_bodyguard",
        photo="https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
        "size=1280x1280&quality=96&"
        "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
        "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album",
        grouping=Groupings.civilians,
        purpose="Тебе нужно защитить собой лучших специалистов",
        message_to_group_after_action="Кто-то пожертвовал собой!",
        message_to_user_after_action="Ты выбрал пожертвовать собой, чтобы спасти {url}",
        mail_message="За кого пожертвовать собой?",
        state_for_waiting_for_action=UserFsm.BODYGUARD_PROTECTS,
    )
    masochist = Role(
        role="Мазохист",
        processed_users_key=None,
        roles_key="masochists",
        photo="https://i.pinimg.com/736x/14/a5/f5/14a5f5eb5dbd73c4707f24d436d80c0b.jpg",
        grouping=Groupings.masochists,
        purpose="Тебе нужно умереть на дневном голосовании.",
    )
    lawyer = Role(
        role="Адвокат",
        roles_key="lawyers",
        last_interactive_key="last_forgiven_by_lawyer",
        processed_users_key="have_alibi",
        photo="https://avatars.mds.yandex.net/get-altay/"
        "5579175/2a0000017e0aa51c3c1fd887206b0156ee34/XXL_height",
        grouping=Groupings.civilians,
        purpose="Тебе нужно защитить мирных жителей от своих же на голосовании.",
        message_to_group_after_action="Кому-то обеспечена защита лучшими адвокатами города!",
        message_to_user_after_action="Ты выбрал защитить {url}",
        mail_message="Кого защитить на голосовании?",
        state_for_waiting_for_action=UserFsm.LAWYER_PROTECTS,
    )
    angel_of_death = Role(
        role="Ангел смерти",
        roles_key="angels_of_death",
        processed_users_key="killed_by_angel_of_death",
        photo="https://avatars.mds.yandex.net/get-entity_search/10844899/935958285/S600xU_2x",
        purpose="Если ты умрешь на голосовании, сможешь ночью забрать кого-нибудь с собой",
        grouping=Groupings.civilians,
        extra_data=[ExtraCache("angels_died", False)],
        message_to_group_after_action="Ангел смерти спускается во имя мести!",
        message_to_user_after_action="Ты выбрал отомстить {url}",
        mail_message="Глупые людишки тебя линчевали, кому ты отомстишь?",
        state_for_waiting_for_action=UserFsm.ANGEL_TAKES_REVENGE,
        for_notifications="angels_died",
    )
    prosecutor = Role(
        role="Прокурор",
        roles_key="prosecutors",
        processed_users_key="cant_vote",
        last_interactive_key="last_arrested_by_prosecutor",
        photo="https://avatars.mds.yandex.net/i?"
        "id=b5115d431dafc24be07a55a8b6343540_l-5205087-images-thumbs&n=13",
        grouping=Groupings.civilians,
        purpose="Тебе нельзя допустить, чтобы днем мафия могла говорить.",
        message_to_group_after_action="По данным разведки потенциальный злоумышленник арестован!",
        message_to_user_after_action="Ты выбрал арестовать {url}",
        mail_message="Кого арестовать этой ночью?",
        state_for_waiting_for_action=UserFsm.PROSECUTOR_ARRESTS,
    )

    civilian = Role(
        role="Мирный житель",
        processed_users_key=None,
        roles_key="civilians",
        photo="https://cdn.culture.ru/c/820179.jpg",
        grouping=Groupings.civilians,
        purpose="Тебе нужно вычислить мафию на голосовании.",
    )
    lucky_gay = Role(
        role="Везунчик",
        processed_users_key=None,
        roles_key="lucky_guys",
        photo="https://avatars.mds.yandex.net/get-mpic/5031100/img_id5520953584482126492.jpeg/orig",
        grouping=Groupings.civilians,
        purpose="Возможно тебе повезет и ты останешься жив после покушения.",
    )
