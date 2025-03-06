import enum
from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    TypedDict,
    TypeAlias,
    NotRequired,
    Literal,
)

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardButton
from telebot.types import InlineKeyboardMarkup

from keyboards.inline.cb.cb_text import DRAW_CB
from keyboards.inline.keypads.mailing import (
    kill_or_check_on_policeman,
)
from states.states import UserFsm
from utils.utils import make_pretty, get_profiles
from utils.validators import (
    are_not_sleeping_killers,
    angel_died_2_nights_ago_or_earlier,
)

Url: TypeAlias = str


class UserGameCache(TypedDict, total=False):
    full_name: str
    url: Url
    role: NotRequired[str]
    pretty_role: NotRequired[str]
    initial_role: str
    enum_name: str
    roles_key: str
    number_died_at_night: int


UserIdStr: TypeAlias = str
UsersInGame: TypeAlias = dict[UserIdStr, UserGameCache]

PlayersIds: TypeAlias = list[int]
LivePlayersIds: TypeAlias = PlayersIds
ChatsAndMessagesIds: TypeAlias = list[list[int]]


class InteractionData(TypedDict):
    sufferers: PlayersIds
    interacting: PlayersIds


TrackingData: TypeAlias = dict[UserIdStr, InteractionData]
NumberOfNight: TypeAlias = int

InteractiveWithHistory: TypeAlias = dict[UserIdStr, NumberOfNight]


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
    killers: PlayersIds

    tracked: PlayersIds
    angels_died: PlayersIds
    killed_by_mafia: PlayersIds
    killed_by_killer: PlayersIds
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

    sleepers: PlayersIds
    cancelled: PlayersIds

    last_treated_by_doctor: InteractiveWithHistory
    last_arrested_by_prosecutor: InteractiveWithHistory
    last_forgiven_by_lawyer: InteractiveWithHistory
    last_self_protected_by_bodyguard: InteractiveWithHistory
    last_tracked_by_agent: InteractiveWithHistory
    last_asleep_by_sleeper: InteractiveWithHistory
    # wait_for: list[int]
    two_voices: PlayersIds

    number_of_night: int


from enum import StrEnum

RolesKeysLiteral = Literal[
    "killers",
    "sleepers",
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
    "last_asleep_by_sleeper",
]


class Groupings(StrEnum):
    criminals = "criminals"
    civilians = "civilians"
    masochists = "masochists"
    suicide_bombers = "suicide_bombers"
    other = "other"


ListToProcessLiteral = Literal[
    "killed_by_killer",
    "cancelled",
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
class Alias:
    role: "AliasesRole"
    is_mass_mailing_list: bool = False

    @staticmethod
    async def boss_is_dead(
        state: FSMContext,
        bot: Bot,
        current_id: int,
        current_enum_name: str,
    ):
        game_data: GameCache = await state.get_data()
        current_enum = Roles[current_enum_name].value
        url = game_data["players"][str(current_id)]["url"]
        role = game_data["players"][str(current_id)]["pretty_role"]

        players = game_data[current_enum.roles_key]
        if not players:
            return
        new_boss_id = players[0]
        new_boss_url = game_data["players"][str(new_boss_id)]["url"]
        game_data["players"][str(new_boss_id)][
            "role"
        ] = current_enum.role
        game_data["players"][str(new_boss_id)]["pretty_role"] = (
            make_pretty(current_enum.role)
        )
        game_data["players"][str(new_boss_id)][
            "enum_name"
        ] = current_enum_name
        await state.set_data(game_data)
        profiles = get_profiles(
            live_players_ids=game_data[current_enum.roles_key],
            players=game_data["players"],
            role=True,
        )
        for player_id in players:
            await bot.send_message(
                chat_id=player_id,
                text=f"Погиб {role} {url}.\n\n"
                f"Новый {role} {new_boss_url}\n\n"
                f"Текущие союзники:\n{profiles}",
            )


@dataclass
class InteractiveWithData:
    mail_message: str
    last_interactive_key: LastProcessedLiteral | None = None
    is_self_selecting: bool = False
    other: int = 1
    self: int = 1

    # mailing_being_sent: Callable | None = None
    # for_notifications: ListToProcessLiteral | None = None

    players_to_send_messages: Callable | None = None
    own_mailing_markup: InlineKeyboardMarkup | None = None


@dataclass
class Role:
    role: str
    roles_key: RolesKeysLiteral
    processed_users_key: ListToProcessLiteral | None
    photo: str
    grouping: str

    purpose: str | Callable | None
    # is_self_selecting: bool = False
    # mail_message: str | None = None
    interactive_with: InteractiveWithData | None = None
    message_to_user_after_action: str | None = None
    message_to_group_after_action: str | None = None
    # interactive_with: InteractiveWithData | None
    # last_interactive_key: LastProcessedLiteral | None = None
    is_mass_mailing_list: bool = False
    extra_data: list[ExtraCache] | None = None
    state_for_waiting_for_action: State | None = None
    # for_notifications: ListToProcessLiteral | None = None
    extra_buttons_for_actions_at_night: tuple[
        InlineKeyboardButton, ...
    ] = ()
    can_kill_at_night_and_survive: bool = False
    # mailing_being_sent: Callable | None = None
    alias: Alias | None = None
    is_alias: bool = False
    # own_mailing_markup: InlineKeyboardMarkup | None = None


class AliasesRole(enum.Enum):
    mafia = Role(
        role="Мафия",
        roles_key="mafias",
        processed_users_key="killed_by_mafia",
        photo="https://i.pinimg.com/736x/a1/10/db/a110db3eaba78bf6423bcea68f330a64.jpg",
        grouping=Groupings.criminals,
        purpose="Тебе нужно уничтожить всех горожан и подчиняться дону.",
        message_to_user_after_action="Ты выбрал убить {url}",
        interactive_with=InteractiveWithData(
            mail_message="Кого убить этой ночью?"
        ),
        # mail_message="Кого убить этой ночью?",
        state_for_waiting_for_action=UserFsm.MAFIA_ATTACKS,
        can_kill_at_night_and_survive=True,
        is_alias=True,
    )
    general = Role(
        role="Генерал",
        roles_key="policeman",
        processed_users_key="killed_by_policeman",
        photo="https://img.clipart-library.com/2/clip-monsters-vs-aliens/clip-monsters-vs-aliens-21.gif",
        grouping=Groupings.civilians,
        purpose="Ты правая рука маршала. В случае его смерти вступишь в должность.",
        state_for_waiting_for_action=UserFsm.POLICEMAN_CHECKS,
        can_kill_at_night_and_survive=True,
        is_alias=True,
    )
    nurse = Role(
        role="Медсестра",
        roles_key="doctors",
        processed_users_key="treated_by_doctor",
        photo="https://cdn.culture.ru/images/e2464a8d-222e-54b1-9016-86f63e902959",
        grouping=Groupings.civilians,
        purpose="Тебе нужно во всем помогать главврачу. "
        "В случае его смерти вступишь в должность.",
        state_for_waiting_for_action=UserFsm.DOCTOR_TREATS,
        is_alias=True,
    )


class Roles(enum.Enum):
    don = Role(
        role="Дон. Высшее звание в преступных группировках",
        roles_key="mafias",
        processed_users_key="killed_by_mafia",
        photo="https://avatars.mds.yandex.net/i?id="
        "a7b2f1eed9cca869784091017f8a66ff_l-7677819-images-thumbs&n=13",
        grouping=Groupings.criminals,
        purpose="Тебе нужно руководить преступниками и убивать мирных.",
        message_to_group_after_action="Мафия выбрала жертву!",
        message_to_user_after_action="Ты выбрал убить {url}",
        extra_data=[ExtraCache("killed_by_don")],
        interactive_with=InteractiveWithData(
            mail_message="Кого убить этой ночью?"
        ),
        # mail_message="Кого убить этой ночью?",
        state_for_waiting_for_action=UserFsm.DON_ATTACKS,
        can_kill_at_night_and_survive=True,
        alias=Alias(
            role=AliasesRole.mafia, is_mass_mailing_list=True
        ),
    )
    doctor = Role(
        role="Главный врач",
        roles_key="doctors",
        processed_users_key="treated_by_doctor",
        interactive_with=InteractiveWithData(
            mail_message="Кого вылечить этой ночью?",
            last_interactive_key="last_treated_by_doctor",
            is_self_selecting=True,
            self=2,
        ),
        # last_interactive_key="last_treated_by_doctor",
        photo="https://gipermed.ru/upload/iblock/4bf/4bfa55f59ceb538bd2c8c437e8f71e5a.jpg",
        grouping=Groupings.civilians,
        purpose="Тебе нужно стараться лечить тех, кому нужна помощь. "
        "Только ты можешь принимать решения.",
        message_to_group_after_action="Доктор спешит кому-то на помощь!",
        message_to_user_after_action="Ты выбрал вылечить {url}",
        # is_self_selecting=True,
        state_for_waiting_for_action=UserFsm.DOCTOR_TREATS,
        alias=Alias(role=AliasesRole.nurse),
    )
    killer = Role(
        role="Наёмный убийца",
        roles_key="killers",
        processed_users_key="killed_by_killer",
        photo="https://steamuserimages-a.akamaihd.net/ugc/633105202506112549/"
        "988D53D1D6BF2FAC4665E453F736C438F601DF6D/"
        "?imw=512&imh=512&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true",
        grouping=Groupings.criminals,
        purpose="Ты убиваешь, кого захочешь, а затем восстанавливаешь свои силы целую ночь.",
        message_to_group_after_action="ЧВК продолжают работать на территории города!",
        message_to_user_after_action="Ты решился ликвидировать {url}",
        interactive_with=InteractiveWithData(
            mail_message="Реши, кому поможешь этой ночью решить проблемы и убить врага!",
            players_to_send_messages=are_not_sleeping_killers,
        ),
        # mail_message="Реши, кому поможешь этой ночью решить проблемы и убить врага!",
        state_for_waiting_for_action=UserFsm.KILLER_ATTACKS,
        can_kill_at_night_and_survive=True,
        # mailing_being_sent=is_not_sleeping_killer,
    )
    sleeper = Role(
        role="Клофелинщица",
        roles_key="sleepers",
        processed_users_key="cancelled",
        interactive_with=InteractiveWithData(
            last_interactive_key="last_asleep_by_sleeper",
            mail_message="Кого усыпить этой ночью?",
        ),
        # last_interactive_key="last_asleep_by_sleeper",
        photo="https://masterpiecer-images.s3.yandex.net/c94e9cb6787b11eeb1ce1e5d9776cfa6:upscaled",
        grouping=Groupings.criminals,
        purpose="Ты можешь усыпить кого-нибудь во имя мафии.",
        message_to_group_after_action="Спят взрослые и дети. Не обошлось и без помощи клофелинщиков!",
        message_to_user_after_action="Ты выбрал усыпить {url}",
        # mail_message="Кого усыпить этой ночью?",
        state_for_waiting_for_action=UserFsm.CLOFFELINE_GIRL_PUTS_TO_SLEEP,
        extra_data=[
            ExtraCache(key="tracking", data_type=dict),
        ],
    )
    policeman = Role(
        role="Маршал. Верховный главнокомандующий армии",
        roles_key="policeman",
        processed_users_key="killed_by_policeman",
        photo="https://avatars.mds.yandex.net/get-kinopoisk-image/"
        "1777765/59ba5e74-7a28-47b2-944a-2788dcd7ebaa/1920x",
        grouping=Groupings.civilians,
        purpose="Тебе нужно вычислить мафию или уничтожить её. Только ты можешь принимать решения.",
        message_to_group_after_action="В город введены войска! Идет перестрелка!",
        message_to_user_after_action="Ты выбрал убить {url}",
        interactive_with=InteractiveWithData(
            mail_message="Какие меры примешь для ликвидации мафии?",
            own_mailing_markup=kill_or_check_on_policeman(),
        ),
        # mail_message="Какие меры примешь для ликвидации мафии?",
        state_for_waiting_for_action=UserFsm.POLICEMAN_CHECKS,
        can_kill_at_night_and_survive=True,
        alias=Alias(role=AliasesRole.general),
        # own_mailing_markup=kill_or_check_on_policeman(),
    )

    agent = Role(
        role="Агент 008",
        processed_users_key="tracked",
        interactive_with=InteractiveWithData(
            last_interactive_key="last_tracked_by_agent",
            mail_message="За кем следить этой ночью?",
        ),
        # last_interactive_key="last_tracked_by_agent",
        roles_key="agents",
        photo="https://avatars.mds.yandex.net/i?id="
        "7b6e30fff5c795d560c07b69e7e9542f044fcaf9e04d4a31-5845211-images-thumbs&n=13",
        grouping=Groupings.civilians,
        purpose="Ты можешь следить за кем-нибудь ночью",
        message_to_group_after_action="Спецслужбы выходят на разведу",
        message_to_user_after_action="Ты выбрал следить за {url}",
        # mail_message="За кем следить этой ночью?",
        state_for_waiting_for_action=UserFsm.AGENT_WATCHES,
        extra_data=[
            ExtraCache(key="tracking", data_type=dict),
        ],
    )
    journalist = Role(
        role="Журналист",
        processed_users_key="talked",
        interactive_with=InteractiveWithData(
            mail_message="У кого взять интервью этой ночью?"
        ),
        roles_key="journalists",
        photo="https://pics.rbc.ru/v2_companies_s3/resized/"
        "960xH/media/company_press_release_image/"
        "022eef78-63a5-4a2b-bb88-e4dcae639e34.jpg",
        grouping=Groupings.civilians,
        purpose="Ты можешь приходить к местным жителям и узнавать, что они видели",
        message_to_group_after_action="Что случилось? Отчаянные СМИ спешат выяснить правду!",
        message_to_user_after_action="Ты выбрал взять интервью у {url}",
        # mail_message="У кого взять интервью этой ночью?",
        state_for_waiting_for_action=UserFsm.JOURNALIST_TAKES_INTERVIEW,
        extra_data=[
            ExtraCache(key="tracking", data_type=dict),
        ],
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
        interactive_with=InteractiveWithData(
            is_self_selecting=True,
            mail_message="Кого повесят сегодня днём?",
            self=0,
            other=0,
        ),
        # is_self_selecting=True,
        # mail_message="Кого повесят сегодня днём?",
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
        interactive_with=InteractiveWithData(
            mail_message="Кого надоумить на неправильный выбор?",
            other=0,
        ),
        # mail_message="Кого надоумить на неправильный выбор?",
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
        interactive_with=InteractiveWithData(
            last_interactive_key="last_self_protected_by_bodyguard",
            mail_message="За кого пожертвовать собой?",
        ),
        # last_interactive_key="last_self_protected_by_bodyguard",
        photo="https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
        "size=1280x1280&quality=96&"
        "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
        "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album",
        grouping=Groupings.civilians,
        purpose="Тебе нужно защитить собой лучших специалистов",
        message_to_group_after_action="Кто-то пожертвовал собой!",
        message_to_user_after_action="Ты выбрал пожертвовать собой, чтобы спасти {url}",
        # mail_message="За кого пожертвовать собой?",
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
        interactive_with=InteractiveWithData(
            last_interactive_key="last_forgiven_by_lawyer",
            mail_message="Кого защитить на голосовании?",
            self=2,
        ),
        # last_interactive_key="last_forgiven_by_lawyer",
        processed_users_key="have_alibi",
        photo="https://avatars.mds.yandex.net/get-altay/"
        "5579175/2a0000017e0aa51c3c1fd887206b0156ee34/XXL_height",
        grouping=Groupings.civilians,
        purpose="Тебе нужно защитить мирных жителей от своих же на голосовании.",
        message_to_group_after_action="Кому-то обеспечена защита лучшими адвокатами города!",
        message_to_user_after_action="Ты выбрал защитить {url}",
        # mail_message="Кого защитить на голосовании?",
        state_for_waiting_for_action=UserFsm.LAWYER_PROTECTS,
    )
    angel_of_death = Role(
        role="Ангел смерти",
        roles_key="angels_of_death",
        processed_users_key="killed_by_angel_of_death",
        interactive_with=InteractiveWithData(
            mail_message="Глупые людишки тебя линчевали, кому ты отомстишь?",
            players_to_send_messages=angel_died_2_nights_ago_or_earlier,
        ),
        photo="https://avatars.mds.yandex.net/get-entity_search/10844899/935958285/S600xU_2x",
        purpose="Если ты умрешь на голосовании, сможешь ночью забрать кого-нибудь с собой",
        grouping=Groupings.civilians,
        extra_data=[ExtraCache("angels_died", False)],
        message_to_user_after_action="Ты выбрал отомстить {url}",
        # mail_message="Глупые людишки тебя линчевали, кому ты отомстишь?",
        state_for_waiting_for_action=UserFsm.ANGEL_TAKES_REVENGE,
        # for_notifications="angels_died",
    )
    prosecutor = Role(
        role="Прокурор",
        roles_key="prosecutors",
        processed_users_key="cant_vote",
        interactive_with=InteractiveWithData(
            last_interactive_key="last_arrested_by_prosecutor",
            mail_message="Кого арестовать этой ночью?",
        ),
        # last_interactive_key="last_arrested_by_prosecutor",
        photo="https://avatars.mds.yandex.net/i?"
        "id=b5115d431dafc24be07a55a8b6343540_l-5205087-images-thumbs&n=13",
        grouping=Groupings.civilians,
        purpose="Тебе нельзя допустить, чтобы днем мафия могла говорить.",
        message_to_group_after_action="По данным разведки потенциальный злоумышленник арестован!",
        message_to_user_after_action="Ты выбрал арестовать {url}",
        # mail_message="Кого арестовать этой ночью?",
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
