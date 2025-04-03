import asyncio
from abc import ABC
from contextlib import suppress
from random import shuffle
from typing import Callable, Optional, Self

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardButton

from cache.cache_types import (
    ExtraCache,
    GameCache,
    PlayersIds,
    LastInteraction,
    UserGameCache,
    RolesLiteral,
)
from constants.output import MONEY_SYM
from database.schemas.results import PersonalResultSchema
from general.groupings import Groupings
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)

from utils.pretty_text import (
    make_pretty,
    make_build,
)
from utils.common import get_the_most_frequently_encountered_id
from utils.informing import get_profiles
from utils.state import get_state_and_assign


class Role(ABC):
    dispatcher: Dispatcher
    bot: Bot
    state: FSMContext
    role: str
    role_id: RolesLiteral
    need_to_process: bool = False
    photo: str
    clearing_state_after_death: bool = True
    grouping: Groupings = Groupings.civilians
    there_may_be_several: bool = False
    purpose: str | Callable | None
    message_to_user_after_action: str | None = None
    message_to_group_after_action: str | None = None
    is_mass_mailing_list: bool = False
    extra_data: list[ExtraCache] | None = None
    state_for_waiting_for_action: State | None = None

    payment_for_treatment = 5
    payment_for_murder = 5
    payment_for_night_spent = 2

    is_alias: bool = False

    def __call__(
        self,
        dispatcher: Dispatcher,
        bot: Bot,
        state: FSMContext,
        all_roles: dict[str, "Role"],
    ):
        self.all_roles = all_roles
        self.dispatcher = dispatcher
        self.bot = bot
        self.state = state
        self.temporary_roles = {}

    async def boss_is_dead(
        self,
        game_data: GameCache,
        current_id: int,
    ):
        url = game_data["players"][str(current_id)]["url"]
        role = game_data["players"][str(current_id)]["pretty_role"]
        role_id = game_data["players"][str(current_id)]["role_id"]
        players = game_data[self.roles_key]
        if not players:
            return
        shuffle(players)
        new_boss_id = players[0]
        new_boss_url = game_data["players"][str(new_boss_id)]["url"]
        game_data["players"][str(new_boss_id)]["pretty_role"] = (
            make_pretty(self.role)
        )
        game_data["players"][str(new_boss_id)]["role_id"] = role_id
        profiles = get_profiles(
            players_ids=game_data[self.roles_key],
            players=game_data["players"],
            role=True,
        )
        tasks = [
            self.bot.send_message(
                chat_id=player_id,
                text=f"Погиб {role} {url}.\n\n"
                f"Новый {role} - {new_boss_url}\n\n"
                f"Текущие союзники:\n{profiles}",
            )
            for player_id in players
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    @classmethod
    @property
    def alias(cls) -> Optional["Role"]:
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
            issubclass(cls, ActiveRoleAtNight)
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
        if winning_group != self.grouping:
            return 0, 0
        return self.grouping.value.payment * (
            len(game_data["players"]) // 4
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
        nights_lived_text = f"Дней и ночей прожито: {nights_lived} из {count_of_nights}"

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
                role=user_data["role"],
                is_winner=True,
                nights_lived=nights_lived,
                money=user_data["money"],
                text=text,
            )
        else:
            user_data["money"] = 0
            text = make_build(
                f"🚫К сожалению, ты проиграл в роли {user_data['initial_role']} (0{MONEY_SYM})!\n\n"
                f"{nights_lived_text} (0{MONEY_SYM})"
            )
            return PersonalResultSchema(
                user_tg_id=int(user_id),
                game_id=game_id,
                role=user_data["role"],
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
        processed_role: Optional["Role"] = None,
        at_night: bool = True,
        additional_players: str | None = None,
    ):
        if self.temporary_roles:
            money = 0
        players = game_data[self.roles_key]
        if additional_players:
            players += game_data[additional_players]
        for player_id in players:
            game_data["players"][str(player_id)]["money"] += money
            if custom_message:
                message = custom_message
            else:
                message = f"{beginning_message} {user_url} ({make_pretty(processed_role.role)})"
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
        self, game_data: GameCache, at_night: bool, user_id: int
    ):
        if at_night:
            message = make_build(
                "К сожалению, тебя убили! Отправь напоследок все, что думаешь!"
            )
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
            )
        else:
            message = make_build("Тебя линчевали на голосовании!")
            await self.bot.send_message(
                chat_id=user_id, text=message
            )


class AliasRole(ABC):
    is_alias = True
    is_mass_mailing_list: bool = False
    there_may_be_several: bool = True

    async def alias_is_dead(
        self, current_id: int, game_data: GameCache
    ):
        url = game_data["players"][str(current_id)]["url"]
        role = game_data["players"][str(current_id)]["pretty_role"]
        profiles = get_profiles(
            players_ids=game_data[self.roles_key],
            players=game_data["players"],
            role=True,
        )
        tasks = [
            self.bot.send_message(
                chat_id=alias_id,
                text=f"Погиб {role} {url}.\n\n"
                f"Текущие союзники:\n{profiles}",
            )
            for alias_id in game_data[self.roles_key]
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

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


class ActiveRoleAtNight(Role):
    state_for_waiting_for_action: State
    was_deceived: bool
    need_to_process: bool = True
    mail_message: str
    need_to_monitor_interaction: bool = True
    is_self_selecting: bool = False
    do_not_choose_others: int = 1
    do_not_choose_self: int = 1
    payment_for_treatment = 10
    payment_for_murder = 10

    def get_money_if_are_not_deceived(
        self, money: int = 9
    ) -> tuple[str, int]:
        additional_text = ""
        if self.was_deceived is True:
            money = 0
            additional_text = " (🚫ОБМАНУТ)"
        else:
            money = money
        return additional_text, money

    @classmethod
    @property
    def notification_message(cls) -> str:
        return f"С тобой этой ночью взаимодействовал {make_pretty(cls.role)}"

    def deleting_notification_messages(
        self, game_data: GameCache, suffer_id: int
    ):
        if self.notification_message:
            game_data["messages_after_night"].remove(
                [suffer_id, self.notification_message]
            )

    def cancel_actions(self, game_data: GameCache, user_id: int):
        suffers = (
            game_data["tracking"]
            .get(str(user_id), {})
            .get("sufferers", [])
        )[:]
        if not suffers:
            return False
        for suffer in suffers:
            self.deleting_notification_messages(
                game_data=game_data, suffer_id=suffer
            )
            if (
                self.processed_users_key
                and suffer in game_data[self.processed_users_key]
            ):
                game_data[self.processed_users_key].remove(suffer)
            with suppress(KeyError, ValueError):
                game_data["tracking"][str(suffer)][
                    "interacting"
                ].remove(user_id)
            with suppress(KeyError, ValueError):
                game_data["tracking"][str(user_id)][
                    "sufferers"
                ].remove(suffer)

        if (
            self.processed_by_boss
            and user_id == game_data[self.roles_key][0]
        ):
            game_data[self.processed_by_boss].clear()

        if self.last_interactive_key:
            data: LastInteraction = game_data[
                self.last_interactive_key
            ]
            if self.is_alias is False:
                for suffer in suffers:
                    suffer_interaction = data[str(suffer)]
                    suffer_interaction.pop()
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
        sent_survey = await self.bot.send_message(
            chat_id=player_id,
            text=self.mail_message,
            reply_markup=markup,
        )
        await self.save_msg_to_delete_and_change_state(
            game_data=game_data,
            player_id=player_id,
            message_id=sent_survey.message_id,
        )

    async def save_msg_to_delete_and_change_state(
        self,
        game_data: GameCache,
        player_id: int,
        message_id: int,
    ):
        game_data["to_delete"].append([player_id, message_id])
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

    def get_roles(self, game_data: GameCache):
        roles = game_data[self.roles_key]
        if not roles:
            return
        return roles

    def get_general_text_before_sending(
        self,
        game_data: GameCache,
    ) -> str | None:
        if self.grouping == Groupings.criminals:
            text = game_data.get("mafias_are_shown")
            if text:
                return f"Известные роли:\n\n{text}"

    @staticmethod
    def allow_sending_mailing(game_data: GameCache):
        return True

    async def mailing(self, game_data: GameCache):
        if self.allow_sending_mailing(game_data) is not True:
            return
        roles = self.get_roles(game_data)
        if not roles:
            return
        general_text = self.get_general_text_before_sending(
            game_data
        )
        if general_text is not None:
            text = make_build(general_text)
            await asyncio.gather(
                *(
                    self.bot.send_message(
                        chat_id=user_id,
                        text=text,
                    )
                    for user_id in roles
                ),
                return_exceptions=True,
            )

        await self.send_survey(
            player_id=roles[0],
            game_data=game_data,
        )
        await self.send_survey_to_aliases(
            roles=roles,
            game_data=game_data,
        )
