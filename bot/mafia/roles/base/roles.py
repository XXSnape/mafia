import asyncio
from abc import ABC, abstractmethod
from contextlib import suppress
from random import shuffle
from typing import TYPE_CHECKING, Callable, Optional, Self

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardButton
from cache.cache_types import (
    GameCache,
    LastInteraction,
    PlayersIds,
    RolesLiteral,
    UserGameCache,
    UserIdInt,
)
from cache.extra import ExtraCache
from database.schemas.results import PersonalResultSchema
from general import settings
from general.groupings import Groupings
from general.text import MONEY_SYM, NUMBER_OF_NIGHT
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from mafia.roles.descriptions.description import RoleDescription
from utils.common import (
    add_message_to_delete,
    get_criminals_ids,
    get_the_most_frequently_encountered_id,
)
from utils.informing import (
    get_profiles,
    remind_criminals_about_inspections,
    send_a_lot_of_messages_safely,
)
from utils.pretty_text import (
    make_build,
    make_pretty,
)
from utils.sorting import sorting_by_rank
from utils.state import get_state_and_assign

if TYPE_CHECKING:
    from general.collection_of_roles import DataWithRoles


class RoleABC(ABC):
    dispatcher: Dispatcher
    bot: Bot
    state: FSMContext
    role: str
    role_id: RolesLiteral
    photo: str
    role_description: RoleDescription
    need_to_process: bool = False
    clearing_state_after_death: bool = True
    grouping: Groupings = Groupings.civilians
    there_may_be_several: bool = False
    purpose: str | Callable | None
    is_mass_mailing_list: bool = False
    extra_data: list[ExtraCache] | None = None
    state_for_waiting_for_action: State | None = None

    payment_for_treatment = 5
    payment_for_murder = 5
    payment_for_night_spent = 4

    is_alias: bool = False

    def __call__(
        self,
        dispatcher: Dispatcher,
        bot: Bot,
        state: FSMContext,
        all_roles: "DataWithRoles",
    ):
        self.all_roles = all_roles
        self.dispatcher = dispatcher
        self.bot = bot
        self.state = state
        self.temporary_roles = {}
        self.dropped_out: set[UserIdInt] = set()
        self.killed_in_afternoon: set[UserIdInt] = set()

    @property
    @abstractmethod
    def role_description(self) -> RoleDescription:
        pass

    def get_general_text_before_sending(
        self,
        game_data: GameCache,
    ) -> str | None:
        if self.grouping == Groupings.criminals:
            return remind_criminals_about_inspections(game_data)
        return None

    def introducing_users_to_roles(self, game_data: GameCache):
        roles_tasks = []
        aliases_tasks = []
        other_tasks = []
        persons = game_data[self.roles_key]
        for number, user_id in enumerate(persons):
            photo = self.photo
            role_name = self.pretty_role
            purpose = self.purpose
            if number != 0 and self.alias:
                photo = self.alias.photo
                role_name = self.alias.pretty_role
                purpose = self.alias.purpose
            roles_tasks.append(
                self.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=f"Твоя роль — "
                    f"{role_name}!\n\n"
                    f"{purpose}",
                    protect_content=game_data["settings"][
                        "protect_content"
                    ],
                )
            )
            if (
                len(game_data[self.roles_key]) > 1
                and self.alias
                and (
                    self.grouping == Groupings.criminals
                    or game_data["settings"]["show_peaceful_allies"]
                )
            ):
                profiles = get_profiles(
                    players_ids=persons,
                    players=game_data["players"],
                    show_current_roles=True,
                    sorting_factory=sorting_by_rank,
                )
                aliases_tasks.append(
                    self.bot.send_message(
                        chat_id=user_id,
                        text=make_build(
                            "❗️Ты и твои союзники, с которыми можно общаться прямо в этом чате:\n"
                        )
                        + profiles,
                        protect_content=game_data["settings"][
                            "protect_content"
                        ],
                    )
                )
            if self.state_for_waiting_for_action:
                roles_tasks.append(
                    get_state_and_assign(
                        dispatcher=self.dispatcher,
                        chat_id=user_id,
                        bot_id=self.bot.id,
                        new_state=self.state_for_waiting_for_action,
                    )
                )
            if self.grouping == Groupings.criminals:
                teammates = [
                    user_id
                    for user_id in get_criminals_ids(game_data)
                    if user_id not in persons
                ]
                if teammates:
                    other_tasks.append(
                        self.bot.send_message(
                            chat_id=user_id,
                            text=make_build(
                                "❗️Сокомандники, с которыми можно общаться прямо в этом чате:\n"
                                + get_profiles(
                                    players_ids=teammates,
                                    players=game_data["players"],
                                    show_current_roles=True,
                                    sorting_factory=sorting_by_rank,
                                )
                            ),
                            protect_content=game_data["settings"][
                                "protect_content"
                            ],
                        )
                    )
        return roles_tasks, aliases_tasks, other_tasks

    def _get_players(self, game_data: GameCache):
        return game_data[self.roles_key]

    async def boss_is_dead(
        self,
        game_data: GameCache,
        current_id: int,
    ):
        players = self._get_players(game_data)
        if not players:
            return
        url = game_data["players"][str(current_id)]["url"]
        role = game_data["players"][str(current_id)]["pretty_role"]
        role_id = game_data["players"][str(current_id)]["role_id"]
        shuffle(players)
        new_boss_id = players[0]
        new_boss_url = game_data["players"][str(new_boss_id)]["url"]
        game_data["players"][str(new_boss_id)][
            "pretty_role"
        ] = self.pretty_role
        game_data["players"][str(new_boss_id)]["role_id"] = role_id
        if (
            self.grouping == Groupings.criminals
            or game_data["settings"]["show_peaceful_allies"]
        ):
            profiles = get_profiles(
                players_ids=game_data[self.roles_key],
                players=game_data["players"],
                show_current_roles=True,
                sorting_factory=sorting_by_rank,
            )
            if self.grouping == Groupings.criminals:
                players = get_criminals_ids(game_data)
                profiles = get_profiles(
                    players_ids=players,
                    players=game_data["players"],
                    show_current_roles=True,
                    sorting_factory=sorting_by_rank,
                )
            await send_a_lot_of_messages_safely(
                bot=self.bot,
                users=players,
                text=f"❗️❗️❗️Погиб {role} — {url}.\n\n"
                f"Новый {role} — {new_boss_url}\n\n"
                f"Все текущие союзники и сокомандники:\n{profiles}",
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
        else:
            await send_a_lot_of_messages_safely(
                bot=self.bot,
                users=[new_boss_id],
                text=f"❗️❗️❗️Погиб {role}.\n\n" f"Ты новый {role}",
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
            text = self.get_general_text_before_sending(game_data)
            if text:
                await send_a_lot_of_messages_safely(
                    bot=self.bot,
                    users=[new_boss_id],
                    text=text,
                    protect_content=game_data["settings"][
                        "protect_content"
                    ],
                )
        if game_data["settings"]["show_roles_after_death"] is False:
            return
        if self.grouping == Groupings.criminals:
            message = (
                "😈Вы думали, на этом все закончится?\n\n"
                "Оу нет! Мои верные союзники уже заняли пост главы криминала!"
            )
        else:
            message = f"😎Встречайте нового {self.pretty_role}!"
        await self.bot.send_photo(
            chat_id=game_data["game_chat"],
            photo=self.photo,
            caption=make_build(message),
        )

    @classmethod
    @property
    def pretty_role(cls) -> str:
        return make_pretty(cls.role) + cls.grouping.value.name[-1]

    @classmethod
    @property
    def alias(cls) -> Optional["RoleABC"]:
        subclasses = cls.__subclasses__()
        if not subclasses:
            return None
        return subclasses[0]()

    @classmethod
    @property
    def roles_key(cls):
        return cls.__name__.lower() + "s"

    @classmethod
    @property
    def processed_users_key(cls):
        if cls.need_to_process:
            return f"processed_by_{cls.__name__.lower()}"

    @classmethod
    @property
    def last_interactive_key(cls):
        if (
            issubclass(cls, ActiveRoleAtNightABC)
            and cls.need_to_monitor_interaction
        ):
            return f"{cls.__name__}_history"

    @classmethod
    @property
    def processed_by_boss(cls):
        if cls.alias and cls.alias.is_mass_mailing_list:
            return f"processed_boss_{cls.__name__}"

    def get_money_for_victory_and_nights(
        self,
        game_data: GameCache,
        winning_group: Groupings,
        nights_lived: int,
        user_id: str,
    ):
        if (winning_group != self.grouping) or int(
            user_id
        ) in self.killed_in_afternoon:
            return 0, 0
        return self.grouping.value.payment * (
            len(game_data["players"])
            // settings.mafia.minimum_number_of_players
        ), (self.payment_for_night_spent * nights_lived)

    def earn_money_for_winning(
        self,
        winning_group: Groupings,
        game_data: GameCache,
        user_id: str,
        game_id: int,
    ) -> PersonalResultSchema:
        user_data = game_data["players"][user_id]
        count_of_nights = game_data["number_of_night"]
        nights_lived = user_data.get(
            "number_died_at_night", count_of_nights
        )
        nights_lived_text = f"⏳Дней и ночей прожито: {nights_lived} из {count_of_nights}"
        if int(user_id) in self.dropped_out:
            money_for_victory, money_for_nights = 0, 0
        else:
            money_for_victory, money_for_nights = (
                self.get_money_for_victory_and_nights(
                    game_data=game_data,
                    winning_group=winning_group,
                    nights_lived=nights_lived,
                    user_id=user_id,
                )
            )
        if money_for_victory:
            user_data["money"] += (
                money_for_victory + money_for_nights
            )
            text = make_build(
                f"🔥🔥🔥Поздравляю! Ты победил в роли {user_data['initial_role']} ({money_for_victory}{MONEY_SYM})!\n\n"
                f"{nights_lived_text} ({money_for_nights}{MONEY_SYM})\n"
            )
            return PersonalResultSchema(
                user_tg_id=int(user_id),
                game_id=game_id,
                role_id=user_data["initial_role_id"],
                is_winner=True,
                nights_lived=nights_lived,
                money=user_data["money"],
                text=text,
            )
        else:
            user_data["money"] = 0
            text = make_build(
                f"🚫К сожалению, ты проиграл в роли {user_data['initial_role']} (0{MONEY_SYM})!\n\n"
                f"{nights_lived_text} (0{MONEY_SYM})\n"
            )
            return PersonalResultSchema(
                user_tg_id=int(user_id),
                game_id=game_id,
                role_id=user_data["initial_role_id"],
                is_winner=False,
                nights_lived=nights_lived,
                money=user_data["money"],
                text=text,
            )

    def get_money_for_voting(
        self,
        voted_role: Self,
    ):
        if self.grouping == Groupings.other:
            return 0
        elif self.grouping != voted_role.grouping:
            return voted_role.payment_for_murder // 2
        else:
            return 0

    def add_money_to_all_allies(
        self,
        game_data: GameCache,
        money: int,
        custom_message: str | None = None,
        beginning_message: str | None = None,
        user_url: str | None = None,
        processed_role: Optional["RoleABC"] = None,
        at_night: bool = True,
        additional_players: PlayersIds | None = None,
    ):
        if self.temporary_roles:
            money = 0
        players = game_data[self.roles_key][:]
        if at_night is False:
            dead_players = set(
                int(user_id) for user_id in game_data["players"]
            ) - set(game_data["live_players_ids"])
            players_with_salary_after_death = []
            for dead_player_id in dead_players:
                number_died_at_night = game_data["players"][
                    str(dead_player_id)
                ]["number_died_at_night"]
                role_id = game_data["players"][str(dead_player_id)][
                    "role_id"
                ]
                if (
                    role_id == self.role_id
                    and game_data["number_of_night"]
                    - 1
                    - number_died_at_night
                    == 0
                ):
                    players_with_salary_after_death.append(
                        dead_player_id
                    )
            players = players + players_with_salary_after_death

        if additional_players:
            players = players + additional_players

        for player_id in players:
            game_data["players"][str(player_id)]["money"] += money
            if custom_message:
                message = custom_message
            else:
                message = f"{beginning_message} {user_url} ({processed_role.pretty_role})"
            message += " - {money}" + MONEY_SYM
            if self.temporary_roles:
                message += " (🚫ОБМАНУТ ВО ВРЕМЯ ИГРЫ)"
            time_of_day = (
                "🌃Ночь" if at_night else "🌟Голосование дня"
            )
            game_data["players"][str(player_id)][
                "achievements"
            ].append(
                [
                    f'{time_of_day} {game_data["number_of_night"]}.\n{message}',
                    money,
                ]
            )
        self.temporary_roles.clear()

    def earn_money_for_voting(
        self,
        voted_role: Self,
        voted_user: UserGameCache,
        game_data: GameCache,
        user_id: int,
    ) -> None:
        user_data = game_data["players"][str(user_id)]
        number_of_day = game_data["number_of_night"]
        earned_money = self.get_money_for_voting(
            voted_role=voted_role
        )
        user_data["money"] += earned_money
        achievements = user_data["achievements"]
        message = (
            (
                f"🌟День {number_of_day}.\nПовешение {voted_user['url']} "
                f"({voted_user['pretty_role']}) - "
            )
            + "{money}"
            + MONEY_SYM
        )
        achievements.append([message, earned_money])

    def get_processed_user_id(self, game_data: GameCache):
        if self.processed_by_boss:
            processed_id = get_the_most_frequently_encountered_id(
                game_data[self.processed_users_key]
            )
            if processed_id is None:
                if not game_data[self.processed_users_key]:
                    return None
                if not game_data[self.processed_by_boss]:
                    return None
                return game_data[self.processed_by_boss][0]
            return processed_id
        if game_data.get(self.processed_users_key):
            return game_data[self.processed_users_key][0]
        return None

    async def report_death(
        self,
        game_data: GameCache,
        at_night: bool | None,
        user_id: UserIdInt,
        message_if_died_especially: str | None = None,
    ):
        if (
            self.grouping == Groupings.criminals
            and self.alias is None
        ):
            criminals = get_criminals_ids(game_data)
            url = game_data["players"][str(user_id)]["url"]
            role = game_data["players"][str(user_id)]["pretty_role"]
            profiles = get_profiles(
                players_ids=criminals,
                players=game_data["players"],
                show_current_roles=True,
                sorting_factory=sorting_by_rank,
            )
            text = f"❗️Погиб {role} — {url}\n\nВсе текущие союзники и сокомандники:\n{profiles}"
            await send_a_lot_of_messages_safely(
                bot=self.bot,
                users=criminals,
                text=text,
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
        if at_night is True:
            message = "😢🌃К сожалению, тебя убили! Отправь напоследок все, что думаешь!"
        elif at_night is False:
            message = (
                "😢🌟К несчастью, тебя линчевали на голосовании!"
            )
            if self.grouping == Groupings.civilians:
                self.killed_in_afternoon.add(user_id)
        else:
            if message_if_died_especially is None:
                message = (
                    "😡Ты выбываешь из игры за неактивность! "
                    "Ты проиграешь вне зависимости от былых заслуг и результатов команды."
                )
                self.dropped_out.add(user_id)
            else:
                message = message_if_died_especially
        await self.bot.send_message(
            chat_id=user_id,
            text=make_build(message),
            protect_content=game_data["settings"]["protect_content"],
        )


class AliasRoleABC(ABC):
    is_alias = True
    is_mass_mailing_list: bool = False
    there_may_be_several: bool = True

    async def alias_is_dead(
        self, current_id: int, game_data: GameCache
    ):
        if (
            self.grouping == Groupings.criminals
            or game_data["settings"]["show_peaceful_allies"] is False
        ):
            return
        url = game_data["players"][str(current_id)]["url"]
        role = game_data["players"][str(current_id)]["pretty_role"]
        profiles = get_profiles(
            players_ids=game_data[self.roles_key],
            players=game_data["players"],
            show_current_roles=True,
        )
        text = f"❗️Погиб {role} — {url}\n\nТекущие сокомандники:\n{profiles}"
        await send_a_lot_of_messages_safely(
            bot=self.bot,
            users=game_data[self.roles_key],
            text=text,
            protect_content=game_data["settings"]["protect_content"],
        )

    @classmethod
    @property
    def roles_key(cls):
        super_classes = cls.__bases__
        return super_classes[1].roles_key

    @classmethod
    @property
    def processed_users_key(cls):
        super_classes = cls.__bases__
        return super_classes[1].processed_users_key

    @classmethod
    @property
    def last_interactive_key(cls):
        super_classes = cls.__bases__
        return super_classes[1].last_interactive_key

    @classmethod
    @property
    def boss_name(cls):
        super_classes = cls.__bases__
        return super_classes[1].pretty_role


class ActiveRoleAtNightABC(RoleABC):
    message_to_user_after_action: str | None = None
    message_to_group_after_action: str | None = None
    words_to_aliases_and_teammates: str | None = None
    state_for_waiting_for_action: State
    was_deceived: bool
    need_to_process: bool = True
    mail_message: str
    need_to_monitor_interaction: bool = True
    is_self_selecting: bool = False
    send_weekend_alerts: bool = True
    do_not_choose_others: int = 1
    do_not_choose_self: int = 1
    payment_for_treatment = 10
    payment_for_murder = 10

    @classmethod
    @property
    def notification_message(cls) -> str:
        return (
            f"С тобой этой ночью взаимодействовал {cls.pretty_role}"
        )

    def leave_notification_message(
        self,
        game_data: GameCache,
    ):
        if self.notification_message:
            processed_user_id = self.get_processed_user_id(game_data)
            if processed_user_id:
                game_data["messages_after_night"].append(
                    [processed_user_id, self.notification_message]
                )

    def _remove_data_from_tracking(
        self, game_data: GameCache, user_id: int
    ):
        sufferers = (
            game_data["tracking"]
            .get(str(user_id), {})
            .get("sufferers", [])
        )[:]
        for sufferer in sufferers:
            if (
                self.processed_users_key
                and sufferer in game_data[self.processed_users_key]
            ):
                game_data[self.processed_users_key].remove(sufferer)
            with suppress(KeyError, ValueError):
                game_data["tracking"][str(sufferer)][
                    "interacting"
                ].remove(user_id)
            with suppress(KeyError, ValueError):
                game_data["tracking"][str(user_id)][
                    "sufferers"
                ].remove(sufferer)
        return sufferers

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if (
            self.alias
            and self.alias.is_mass_mailing_list
            and user_id == game_data[self.roles_key][0]
        ):
            game_data[self.processed_by_boss].clear()
            is_sedated = bool(game_data[self.processed_users_key])
            sufferers = self._remove_data_from_tracking(
                game_data=game_data, user_id=user_id
            )
            message_to_aliases = (
                f"{self.pretty_role} "
                f"{game_data['players'][str(user_id)]['url']} "
                f"был усыплён, поэтому вся команда не вышла на работу ночью"
            )
            for alias_id in game_data[self.roles_key][1:]:
                self._remove_data_from_tracking(
                    game_data=game_data, user_id=alias_id
                )
                game_data["messages_after_night"].append(
                    [alias_id, message_to_aliases]
                )
        else:
            sufferers = self._remove_data_from_tracking(
                game_data=game_data, user_id=user_id
            )
            is_sedated = bool(sufferers)
        if not is_sedated:
            return False
        if self.last_interactive_key:
            data: LastInteraction = game_data[
                self.last_interactive_key
            ]
            if self.is_alias is False:
                for sufferer in sufferers:
                    sufferer_interaction = data[str(sufferer)]
                    sufferer_interaction.pop()
        return True

    async def send_survey(
        self,
        player_id: int,
        game_data: GameCache,
    ):

        markup = self.generate_markup(
            player_id=player_id,
            game_data=game_data,
        )
        game_data["waiting_for_action_at_night"].append(player_id)
        with suppress(TelegramAPIError):
            sent_survey = await self.bot.send_message(
                chat_id=player_id,
                text=self.mail_message,
                reply_markup=markup,
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
            await self.save_information_about_mail_and_change_state(
                game_data=game_data,
                player_id=player_id,
                message_id=sent_survey.message_id,
            )

    async def save_information_about_mail_and_change_state(
        self,
        game_data: GameCache,
        player_id: int,
        message_id: int,
    ):
        add_message_to_delete(
            game_data=game_data,
            chat_id=player_id,
            message_id=message_id,
        )
        await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=player_id,
            bot_id=self.bot.id,
            new_state=self.state_for_waiting_for_action,
        )

    async def send_survey_to_aliases(
        self,
        roles: PlayersIds,
        game_data: GameCache,
    ):
        tasks = []
        if self.alias and len(roles) > 1:
            for user_id in roles[1:]:
                if self.alias.is_mass_mailing_list:
                    tasks.append(
                        self.send_survey(
                            player_id=user_id,
                            game_data=game_data,
                        )
                    )
        await asyncio.gather(*tasks, return_exceptions=True)

    def generate_markup(
        self,
        player_id: int,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        exclude = []
        current_number = game_data["number_of_night"]
        if self.is_self_selecting is False:
            exclude = [player_id]
        for processed_user_id, numbers in game_data.get(
            self.last_interactive_key, {}
        ).items():
            if not numbers:
                continue
            last_number_of_night = numbers[-1]
            if int(processed_user_id) == player_id:
                constraint = self.do_not_choose_self
            else:
                constraint = self.do_not_choose_others
            if constraint is None:
                exclude.append(int(processed_user_id))
            elif (
                current_number - last_number_of_night
                < constraint + 1
            ):
                exclude.append(int(processed_user_id))

        if game_data["live_players_ids"] == exclude:
            return
        return send_selection_to_players_kb(
            players_ids=game_data["live_players_ids"],
            players=game_data["players"],
            exclude=exclude,
            extra_buttons=extra_buttons,
        )

    @staticmethod
    def allow_sending_mailing(game_data: GameCache) -> bool:
        return True

    async def mailing(self, game_data: GameCache):
        roles = game_data[self.roles_key]
        if not roles:
            return
        if self.allow_sending_mailing(game_data) is not True:
            if self.send_weekend_alerts is False:
                return
            text = (
                NUMBER_OF_NIGHT.format(game_data["number_of_night"])
                + "😜У тебя сегодня выходной!"
            )
            await send_a_lot_of_messages_safely(
                bot=self.bot,
                users=[roles[0]],
                text=make_build(text),
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
            return
        general_text = self.get_general_text_before_sending(
            game_data
        )
        if general_text is not None:
            text = make_build(general_text)
            users = (
                roles
                if self.grouping == Groupings.criminals
                or game_data["settings"]["show_peaceful_allies"]
                else [roles[0]]
            )
            await send_a_lot_of_messages_safely(
                bot=self.bot,
                users=users,
                text=text,
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )

        await self.send_survey(
            player_id=roles[0],
            game_data=game_data,
        )
        await self.send_survey_to_aliases(
            roles=roles,
            game_data=game_data,
        )
