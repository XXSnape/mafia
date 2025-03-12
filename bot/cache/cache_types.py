from dataclasses import dataclass
from typing import NotRequired, TypeAlias, TypedDict

# @dataclass
# class Role:
#     role: str
#     roles_key: RolesKeysLiteral
#     processed_users_key: ListToProcessLiteral | None
#     photo: str
#     grouping: str
#
#     purpose: str | Callable | None
#     # is_self_selecting: bool = False
#     # mail_message: str | None = None
#     interactive_with: InteractiveWithData | None = None
#     message_to_user_after_action: str | None = None
#     message_to_group_after_action: str | None = None
#     # interactive_with: InteractiveWithData | None
#     # last_interactive_key: LastProcessedLiteral | None = None
#     is_mass_mailing_list: bool = False
#     extra_data: list[ExtraCache] | None = None
#     state_for_waiting_for_action: State | None = None
#     # for_notifications: ListToProcessLiteral | None = None
#     extra_buttons_for_actions_at_night: tuple[
#         InlineKeyboardButton, ...
#     ] = ()
#     can_kill_at_night_and_survive: bool = False
#     # mailing_being_sent: Callable | None = None
#     alias: Alias | None = None
#     is_alias: bool = False
# own_mailing_markup: InlineKeyboardMarkup | None = None


# class AliasesRole(enum.Enum):
#     mafia = Role(
#         role="Мафия",
#         roles_key="mafias",
#         processed_users_key="killed_by_mafia",
#         photo="https://i.pinimg.com/736x/a1/10/db/a110db3eaba78bf6423bcea68f330a64.jpg",
#         grouping=Groupings.criminals,
#         purpose="Тебе нужно уничтожить всех горожан и подчиняться дону.",
#         message_to_user_after_action="Ты выбрал убить {url}",
#         interactive_with=InteractiveWithData(
#             mail_message="Кого убить этой ночью?"
#         ),
#         # mail_message="Кого убить этой ночью?",
#         state_for_waiting_for_action=UserFsm.MAFIA_ATTACKS,
#         can_kill_at_night_and_survive=True,
#         is_alias=True,
#     )
#
#     general = Role(
#         role="Генерал",
#         roles_key="policeman",
#         processed_users_key="killed_by_policeman",
#         photo="https://img.clipart-library.com/2/clip-monsters-vs-aliens/clip-monsters-vs-aliens-21.gif",
#         grouping=Groupings.civilians,
#         purpose="Ты правая рука маршала. В случае его смерти вступишь в должность.",
#         state_for_waiting_for_action=UserFsm.POLICEMAN_CHECKS,
#         can_kill_at_night_and_survive=True,
#         is_alias=True,
#     )
#     nurse = Role(
#         role="Медсестра",
#         roles_key="doctors",
#         processed_users_key="treated_by_doctor",
#         photo="https://cdn.culture.ru/images/e2464a8d-222e-54b1-9016-86f63e902959",
#         grouping=Groupings.civilians,
#         purpose="Тебе нужно во всем помогать главврачу. "
#         "В случае его смерти вступишь в должность.",
#         state_for_waiting_for_action=UserFsm.DOCTOR_TREATS,
#         is_alias=True,
#     )


# class Roles(enum.Enum):
#     don = Role(
#         role="Дон. Высшее звание в преступных группировках",
#         roles_key="mafias",
#         processed_users_key="killed_by_mafia",
#         photo="https://avatars.mds.yandex.net/i?id="
#         "a7b2f1eed9cca869784091017f8a66ff_l-7677819-images-thumbs&n=13",
#         grouping=Groupings.criminals,
#         purpose="Тебе нужно руководить преступниками и убивать мирных.",
#         message_to_group_after_action="Мафия выбрала жертву!",
#         message_to_user_after_action="Ты выбрал убить {url}",
#         extra_data=[ExtraCache("killed_by_don")],
#         interactive_with=InteractiveWithData(
#             mail_message="Кого убить этой ночью?"
#         ),
#         # mail_message="Кого убить этой ночью?",
#         state_for_waiting_for_action=UserFsm.DON_ATTACKS,
#         can_kill_at_night_and_survive=True,
#         alias=Alias(
#             role=AliasesRole.mafia, is_mass_mailing_list=True
#         ),
#     )
#     traitor = Role(
#         role="Госизменщик",
#         roles_key="traitors",
#         processed_users_key=None,
#         photo="https://i.playground.ru/p/sLHLRFjDy8_89wYe26RIQw.jpeg",
#         grouping=Groupings.criminals,
#         purpose="Ты можешь просыпаться каждую 2-ую ночь и узнавать роль других игроков для .",
#         message_to_group_after_action="Мафия и Даркнет. Что может сочетаться лучше?"
#         " Поддельные ксивы помогают узнавать правду!",
#         message_to_user_after_action="Ты выбрал узнать роль {url}",
#         interactive_with=InteractiveWithData(
#             mail_message="Кого проверишь для мафии?",
#             players_to_send_messages=are_not_sleeping_traits,
#         ),
#         state_for_waiting_for_action=UserFsm.TRAITOR_FINDS_OUT,
#     )
#     killer = Role(
#         role="Наёмный убийца",
#         roles_key="killers",
#         processed_users_key="killed_by_killer",
#         photo="https://steamuserimages-a.akamaihd.net/ugc/633105202506112549/"
#         "988D53D1D6BF2FAC4665E453F736C438F601DF6D/"
#         "?imw=512&imh=512&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true",
#         grouping=Groupings.criminals,
#         purpose="Ты убиваешь, кого захочешь, а затем восстанавливаешь свои силы целую ночь.",
#         message_to_group_after_action="ЧВК продолжают работать на территории города!",
#         message_to_user_after_action="Ты решился ликвидировать {url}",
#         interactive_with=InteractiveWithData(
#             mail_message="Реши, кому поможешь этой ночью решить проблемы и убить врага!",
#             players_to_send_messages=are_not_sleeping_killers,
#         ),
#         # mail_message="Реши, кому поможешь этой ночью решить проблемы и убить врага!",
#         state_for_waiting_for_action=UserFsm.KILLER_ATTACKS,
#         can_kill_at_night_and_survive=True,
#         # mailing_being_sent=is_not_sleeping_killer,
#     )
#     werewolf = Role(
#         role="Оборотень",
#         roles_key="werewolves",
#         processed_users_key=None,
#         photo="https://sun9-42.userapi.com/impf/c303604/v303604068/"
#         "170c/FXQRtSk8e28.jpg?size=484x604&quality=96&sign=bf5555ef2b801954b0b92848975525fd&type=album"
#         "?imw=512&imh=512&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true",
#         grouping=Groupings.civilians,
#         purpose="На 4 ночь ты сможешь превратиться в мафию, маршала или доктора.",
#         # message_to_group_after_action="Кто-то совершает ",
#         # message_to_user_after_action="Ты решился ликвидировать {url}",
#         interactive_with=InteractiveWithData(
#             mail_message="Реши, в кого сегодня превратишься!",
#             players_to_send_messages=is_4_at_night,
#             own_mailing_markup=send_transformation_kb,
#         ),
#         # mail_message="Реши, кому поможешь этой ночью решить проблемы и убить врага!",
#         state_for_waiting_for_action=UserFsm.WEREWOLF_TURNS_INTO,
#     )
#     policeman = Role(
#         role="Маршал. Верховный главнокомандующий армии",
#         roles_key="policeman",
#         processed_users_key="killed_by_policeman",
#         photo="https://avatars.mds.yandex.net/get-kinopoisk-image/"
#         "1777765/59ba5e74-7a28-47b2-944a-2788dcd7ebaa/1920x",
#         grouping=Groupings.civilians,
#         purpose="Тебе нужно вычислить мафию или уничтожить её. Только ты можешь принимать решения.",
#         message_to_group_after_action="В город введены войска! Идет перестрелка!",
#         message_to_user_after_action="Ты выбрал убить {url}",
#         interactive_with=InteractiveWithData(
#             mail_message="Какие меры примешь для ликвидации мафии?",
#             own_mailing_markup=kill_or_check_on_policeman(),
#             additional_text_func=remind_commissioner_about_inspections,
#         ),
#         # mail_message="Какие меры примешь для ликвидации мафии?",
#         state_for_waiting_for_action=UserFsm.POLICEMAN_CHECKS,
#         can_kill_at_night_and_survive=True,
#         alias=Alias(role=AliasesRole.general),
#         extra_data=[
#             ExtraCache(key="disclosed_roles"),
#             ExtraCache(
#                 key="text_about_checks",
#                 is_cleared=False,
#                 data_type=str,
#             ),
#         ],
#         # own_mailing_markup=kill_or_check_on_policeman(),
#     )
#     doctor = Role(
#         role="Главный врач",
#         roles_key="doctors",
#         processed_users_key="treated_by_doctor",
#         interactive_with=InteractiveWithData(
#             mail_message="Кого вылечить этой ночью?",
#             last_interactive_key="last_treated_by_doctor",
#             is_self_selecting=True,
#             self=2,
#         ),
#         # last_interactive_key="last_treated_by_doctor",
#         photo="https://gipermed.ru/upload/iblock/4bf/4bfa55f59ceb538bd2c8c437e8f71e5a.jpg",
#         grouping=Groupings.civilians,
#         purpose="Тебе нужно стараться лечить тех, кому нужна помощь. "
#         "Только ты можешь принимать решения.",
#         message_to_group_after_action="Доктор спешит кому-то на помощь!",
#         message_to_user_after_action="Ты выбрал вылечить {url}",
#         # is_self_selecting=True,
#         state_for_waiting_for_action=UserFsm.DOCTOR_TREATS,
#         alias=Alias(role=AliasesRole.nurse),
#     )
#     forger = Role(
#         role="Румпельштильцхен",
#         roles_key="forgers",
#         grouping=Groupings.criminals,
#         purpose="Ты должен обманывать комиссара и подделывать документы на свое усмотрение во имя мафии",
#         message_to_group_after_action="Говорят, в лесах завелись персонажи из Шрека, "
#         "подговорённые мафией, дискоординирующие государственную армию!",
#         photo="https://sun9-64.userapi.com/impg/R8WBtzZkQKycXDW5YCvKXUJB03XJnboRa0LDHw/"
#         "yo9Ng0yPqa0.jpg?size=604x302&quality=95&sign"
#         "=0fb255f26d2fd1775b2db1c2001f7a0b&type=album",
#         state_for_waiting_for_action=UserFsm.FORGER_FAKES,
#         processed_users_key=None,
#         interactive_with=InteractiveWithData(
#             last_interactive_key="last_forgers",
#             mail_message="Кому сегодня подделаешь документы?",
#             is_self_selecting=True,
#             self=2,
#             other=2,
#         ),
#         extra_data=[ExtraCache(key="forged_roles")],
#     )
#     hacker = Role(
#         role="Хакер",
#         roles_key="hackers",
#         processed_users_key=None,
#         photo="https://i.pinimg.com/originals/d0/e0/b5/d0e0b5198b0ea334fa243b9afd459f6b.png",
#         grouping=Groupings.civilians,
#         purpose="Ты можешь прослушивать диалоги мафии и узнавать, за кого они голосуют",
#     )
#     sleeper = Role(
#         role="Клофелинщица",
#         roles_key="sleepers",
#         processed_users_key="cancelled",
#         interactive_with=InteractiveWithData(
#             last_interactive_key="last_asleep_by_sleeper",
#             mail_message="Кого усыпить этой ночью?",
#         ),
#         # last_interactive_key="last_asleep_by_sleeper",
#         photo="https://masterpiecer-images.s3.yandex.net/c94e9cb6787b11eeb1ce1e5d9776cfa6:upscaled",
#         grouping=Groupings.criminals,
#         purpose="Ты можешь усыпить кого-нибудь во имя мафии.",
#         message_to_group_after_action="Спят взрослые и дети. Не обошлось и без помощи клофелинщиков!",
#         message_to_user_after_action="Ты выбрал усыпить {url}",
#         # mail_message="Кого усыпить этой ночью?",
#         state_for_waiting_for_action=UserFsm.CLOFFELINE_GIRL_PUTS_TO_SLEEP,
#         extra_data=[
#             ExtraCache(key="tracking", data_type=dict),
#         ],
#     )
#
#     agent = Role(
#         role="Агент 008",
#         processed_users_key="tracked",
#         interactive_with=InteractiveWithData(
#             last_interactive_key="last_tracked_by_agent",
#             mail_message="За кем следить этой ночью?",
#         ),
#         # last_interactive_key="last_tracked_by_agent",
#         roles_key="agents",
#         photo="https://avatars.mds.yandex.net/i?id="
#         "7b6e30fff5c795d560c07b69e7e9542f044fcaf9e04d4a31-5845211-images-thumbs&n=13",
#         grouping=Groupings.civilians,
#         purpose="Ты можешь следить за кем-нибудь ночью",
#         message_to_group_after_action="Спецслужбы выходят на разведу",
#         message_to_user_after_action="Ты выбрал следить за {url}",
#         # mail_message="За кем следить этой ночью?",
#         state_for_waiting_for_action=UserFsm.AGENT_WATCHES,
#         extra_data=[
#             ExtraCache(key="tracking", data_type=dict),
#         ],
#     )
#     journalist = Role(
#         role="Журналист",
#         processed_users_key="talked",
#         interactive_with=InteractiveWithData(
#             mail_message="У кого взять интервью этой ночью?"
#         ),
#         roles_key="journalists",
#         photo="https://pics.rbc.ru/v2_companies_s3/resized/"
#         "960xH/media/company_press_release_image/"
#         "022eef78-63a5-4a2b-bb88-e4dcae639e34.jpg",
#         grouping=Groupings.civilians,
#         purpose="Ты можешь приходить к местным жителям и узнавать, что они видели",
#         message_to_group_after_action="Что случилось? Отчаянные СМИ спешат выяснить правду!",
#         message_to_user_after_action="Ты выбрал взять интервью у {url}",
#         # mail_message="У кого взять интервью этой ночью?",
#         state_for_waiting_for_action=UserFsm.JOURNALIST_TAKES_INTERVIEW,
#         extra_data=[
#             ExtraCache(key="tracking", data_type=dict),
#         ],
#     )
#
#     punisher = Role(
#         role="Каратель",
#         processed_users_key=None,
#         roles_key="punishers",
#         photo="https://lastfm.freetls.fastly.net/i/u/ar0/d04cdfdf3f65412bc1e7870ec6599ed7.png",
#         grouping=Groupings.civilians,
#         purpose="Спровоцируй мафию и забери её с собой!",
#     )
#
#     analyst = Role(
#         role="Политический аналитик",
#         processed_users_key="predicted",
#         roles_key="analysts",
#         photo="https://habrastorage.org/files/2e3/371/6a2/2e33716a2bb74f8eb67378334960ebb5.png",
#         grouping=Groupings.civilians,
#         purpose="Тебе нужно на основе ранее полученных данных предсказать, кого повесят на дневном голосовании",
#         interactive_with=InteractiveWithData(
#             is_self_selecting=True,
#             mail_message="Кого повесят сегодня днём?",
#             self=0,
#             other=0,
#         ),
#         # is_self_selecting=True,
#         # mail_message="Кого повесят сегодня днём?",
#         message_to_group_after_action="Составляется прогноз на завтрашний день",
#         message_to_user_after_action="Ты предположил, что повесят {url}",
#         extra_buttons_for_actions_at_night=(
#             InlineKeyboardButton(
#                 text="У жителей не хватит политической воли",
#                 callback_data=DRAW_CB,
#             ),
#         ),
#         state_for_waiting_for_action=UserFsm.ANALYST_ASSUMES,
#     )
#     suicide_bomber = Role(
#         role="Ночной смертник",
#         roles_key="suicide_bombers",
#         processed_users_key=None,
#         photo="https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
#         "size=1280x1280&quality=96&"
#         "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
#         "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album",
#         grouping=Groupings.suicide_bombers,
#         purpose="Тебе нужно умереть ночью.",
#     )
#     instigator = Role(
#         role="Подстрекатель",
#         roles_key="instigators",
#         processed_users_key="missed",
#         photo="https://avatars.dzeninfra.ru/get-zen_doc/3469057/"
#         "pub_620655d2a7947c53d6c601a2_620671b4b495be46b12c0a0c/scale_1200",
#         grouping=Groupings.other,
#         purpose="Твоя жертва всегда ошибется при выборе на голосовании.",
#         message_to_group_after_action="Кажется, кто-то становится жертвой психологического насилия!",
#         message_to_user_after_action="Ты выбрал прополоскать мозги {url}",
#         interactive_with=InteractiveWithData(
#             mail_message="Кого надоумить на неправильный выбор?",
#             other=0,
#         ),
#         # mail_message="Кого надоумить на неправильный выбор?",
#         state_for_waiting_for_action=UserFsm.INSTIGATOR_LYING,
#     )
#     prime_minister = Role(
#         role="Премьер-министр",
#         roles_key="prime_ministers",
#         processed_users_key="voted_by_prime",
#         photo="https://avatars.mds.yandex.net/i?id=fb2e5e825d183d5344d93bc5636bc4c4_l-5084109-images-thumbs&n=13",
#         grouping=Groupings.civilians,
#         purpose="Твой голос стоит как 2!",
#     )
#     bodyguard = Role(
#         role="Телохранитель",
#         roles_key="bodyguards",
#         processed_users_key="treated_by_bodyguard",
#         interactive_with=InteractiveWithData(
#             last_interactive_key="last_self_protected_by_bodyguard",
#             mail_message="За кого пожертвовать собой?",
#         ),
#         # last_interactive_key="last_self_protected_by_bodyguard",
#         photo="https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
#         "size=1280x1280&quality=96&"
#         "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
#         "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album",
#         grouping=Groupings.civilians,
#         purpose="Тебе нужно защитить собой лучших специалистов",
#         message_to_group_after_action="Кто-то пожертвовал собой!",
#         message_to_user_after_action="Ты выбрал пожертвовать собой, чтобы спасти {url}",
#         # mail_message="За кого пожертвовать собой?",
#         state_for_waiting_for_action=UserFsm.BODYGUARD_PROTECTS,
#     )
#     masochist = Role(
#         role="Мазохист",
#         processed_users_key=None,
#         roles_key="masochists",
#         photo="https://i.pinimg.com/736x/14/a5/f5/14a5f5eb5dbd73c4707f24d436d80c0b.jpg",
#         grouping=Groupings.masochists,
#         purpose="Тебе нужно умереть на дневном голосовании.",
#     )
#     lawyer = Role(
#         role="Адвокат",
#         roles_key="lawyers",
#         interactive_with=InteractiveWithData(
#             last_interactive_key="last_forgiven_by_lawyer",
#             mail_message="Кого защитить на голосовании?",
#             self=2,
#         ),
#         # last_interactive_key="last_forgiven_by_lawyer",
#         processed_users_key="have_alibi",
#         photo="https://avatars.mds.yandex.net/get-altay/"
#         "5579175/2a0000017e0aa51c3c1fd887206b0156ee34/XXL_height",
#         grouping=Groupings.civilians,
#         purpose="Тебе нужно защитить мирных жителей от своих же на голосовании.",
#         message_to_group_after_action="Кому-то обеспечена защита лучшими адвокатами города!",
#         message_to_user_after_action="Ты выбрал защитить {url}",
#         # mail_message="Кого защитить на голосовании?",
#         state_for_waiting_for_action=UserFsm.LAWYER_PROTECTS,
#     )
#     angel_of_death = Role(
#         role="Ангел смерти",
#         roles_key="angels_of_death",
#         processed_users_key="killed_by_angel_of_death",
#         interactive_with=InteractiveWithData(
#             mail_message="Глупые людишки тебя линчевали, кому ты отомстишь?",
#             players_to_send_messages=angel_died_2_nights_ago_or_earlier,
#         ),
#         photo="https://avatars.mds.yandex.net/get-entity_search/10844899/935958285/S600xU_2x",
#         purpose="Если ты умрешь на голосовании, сможешь ночью забрать кого-нибудь с собой",
#         grouping=Groupings.civilians,
#         extra_data=[ExtraCache("angels_died", False)],
#         message_to_user_after_action="Ты выбрал отомстить {url}",
#         # mail_message="Глупые людишки тебя линчевали, кому ты отомстишь?",
#         state_for_waiting_for_action=UserFsm.ANGEL_TAKES_REVENGE,
#         # for_notifications="angels_died",
#     )
#     prosecutor = Role(
#         role="Прокурор",
#         roles_key="prosecutors",
#         processed_users_key="cant_vote",
#         interactive_with=InteractiveWithData(
#             last_interactive_key="last_arrested_by_prosecutor",
#             mail_message="Кого арестовать этой ночью?",
#         ),
#         # last_interactive_key="last_arrested_by_prosecutor",
#         photo="https://avatars.mds.yandex.net/i?"
#         "id=b5115d431dafc24be07a55a8b6343540_l-5205087-images-thumbs&n=13",
#         grouping=Groupings.civilians,
#         purpose="Тебе нельзя допустить, чтобы днем мафия могла говорить.",
#         message_to_group_after_action="По данным разведки потенциальный злоумышленник арестован!",
#         message_to_user_after_action="Ты выбрал арестовать {url}",
#         # mail_message="Кого арестовать этой ночью?",
#         state_for_waiting_for_action=UserFsm.PROSECUTOR_ARRESTS,
#     )
#
#     civilian = Role(
#         role="Мирный житель",
#         processed_users_key=None,
#         roles_key="civilians",
#         photo="https://cdn.culture.ru/c/820179.jpg",
#         grouping=Groupings.civilians,
#         purpose="Тебе нужно вычислить мафию на голосовании.",
#     )
#
#     lucky_gay = Role(
#         role="Везунчик",
#         processed_users_key=None,
#         roles_key="lucky_guys",
#         photo="https://avatars.mds.yandex.net/get-mpic/5031100/img_id5520953584482126492.jpeg/orig",
#         grouping=Groupings.civilians,
#         purpose="Возможно тебе повезет и ты останешься жив после покушения.",
#     )


@dataclass
class ExtraCache:
    key: str
    is_cleared: bool = True
    data_type: type = list


Url: TypeAlias = str
PlayersIds: TypeAlias = list[int]
UserIdStr: TypeAlias = str
Role: TypeAlias = str
UserIdInt: TypeAlias = int
Message: TypeAlias = str


class UserGameCache(TypedDict, total=False):
    full_name: str
    url: Url
    role: NotRequired[Role]
    pretty_role: NotRequired[str]
    initial_role: str
    enum_name: str
    roles_key: str
    number_died_at_night: int
    user_id: int


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
DisclosedRoles = list[list[UserIdStr, Role]]
VotedFor: TypeAlias = list[list[UserIdInt]]


class UserCache(TypedDict):
    game_chat: int


class GameCache(TypedDict, total=True):
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
