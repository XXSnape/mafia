from abc import ABC
from typing import Callable, Optional

from aiogram import Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from telebot.types import InlineKeyboardButton

from cache.cache_types import ExtraCache, GameCache, PlayersIds
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from states.states import UserFsm
from utils.utils import (
    get_profiles,
    get_state_and_assign,
    get_the_most_frequently_encountered_id,
)
from utils.validators import get_object_id_if_exists


class Role(ABC):
    dispatcher: Dispatcher
    bot: Bot
    state: FSMContext
    role: str
    need_to_process: bool = False
    photo: str
    grouping: str
    purpose: str | Callable | None
    message_to_user_after_action: str | None = None
    message_to_group_after_action: str | None = None
    is_mass_mailing_list: bool = False
    extra_data: list[ExtraCache] | None = None
    state_for_waiting_for_action: State | None = None
    can_kill_at_night: bool = False
    can_treat: bool = False

    alias: Optional["AliasRole"] = None

    is_alias: bool = False

    def __call__(
        self, dispatcher: Dispatcher, bot: Bot, state: FSMContext
    ):
        self.dispatcher = dispatcher
        self.bot = bot
        self.state = state

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
        self, game_data: GameCache, is_night: bool, user_id: int
    ):
        if is_night:
            message = "К сожалению, тебя убили! Отправь напоследок все, что думаешь!"
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
            )
        else:
            message = "Тебя линчевали на голосовании!"
            await self.bot.send_message(
                chat_id=user_id, text=message
            )


class AliasRole(Role):
    is_alias = True
    is_mass_mailing_list: bool = False

    async def alias_is_dead(
        self, current_id: int, game_data: GameCache
    ):
        url = game_data["players"][str(current_id)]["url"]
        role = game_data["players"][str(current_id)]["pretty_role"]
        profiles = get_profiles(
            live_players_ids=game_data[self.roles_key],
            players=game_data["players"],
            role=True,
        )
        for alias_id in game_data[self.roles_key]:
            await self.bot.send_message(
                chat_id=alias_id,
                text=f"Погиб {role} {url}.\n\n"
                f"Текущие союзники:\n{profiles}",
            )


class ActiveRoleAtNight(Role):
    state_for_waiting_for_action: State
    need_to_process: bool = True
    mail_message: str
    need_to_monitor_interaction: bool = True
    is_self_selecting: bool = False
    do_not_choose_others: int = 1
    do_not_choose_self: int = 1

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
        if self.alias and len(roles) > 1:
            for user_id in roles[1:]:
                if self.alias.is_mass_mailing_list:
                    await self.send_survey(
                        player_id=user_id,
                        game_data=game_data,
                    )

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
        for processed_user_id, number in game_data.get(
            self.last_interactive_key, {}
        ).items():
            if int(processed_user_id) == player_id:
                constraint = self.do_not_choose_self
            else:
                constraint = self.do_not_choose_others
            if constraint is None:
                exclude.append(int(processed_user_id))
            elif (current_number - number) < constraint + 1:
                exclude.append(int(processed_user_id))
        if game_data["players_ids"] == exclude:
            return
        return send_selection_to_players_kb(
            players_ids=game_data["players_ids"],
            players=game_data["players"],
            exclude=exclude,
            extra_buttons=extra_buttons,
        )

    async def mailing(self, game_data: GameCache):
        if self.processed_users_key not in game_data:
            return
        roles = game_data[self.roles_key]
        if not roles:
            return
        await self.send_survey(
            player_id=roles[0],
            game_data=game_data,
        )
        await self.send_survey_to_aliases(
            roles=roles,
            game_data=game_data,
        )
