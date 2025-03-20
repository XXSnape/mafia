import asyncio
from collections.abc import Callable
from contextlib import suppress
from operator import attrgetter
from typing import TYPE_CHECKING

from aiogram import Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.cache_types import (
    ChatsAndMessagesIds,
    GameCache,
    UserGameCache,
    LastInteraction,
)
from general.exceptions import GameIsOver
from .roles.base.roles import Groupings
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from services.mailing import MailerToPlayers
from states.states import GameFsm, UserFsm
from utils.utils import (
    get_state_and_assign,
    get_the_most_frequently_encountered_id,
    get_results_of_goal_identification,
    get_results_of_voting,
)

from .protocols.protocols import (
    VictimsOfVote,
)
from .roles import Mafia, Killer
from .roles.base import AliasRole, BossIsDeadMixin, Role
from .roles.base.mixins import ProcedureAfterNight

if TYPE_CHECKING:
    from .pipeline_game import Game


def check_end_of_game(async_func: Callable):
    async def wrapper(self: "Game"):
        result = await async_func(self)
        state = self.state
        game_data: GameCache = await state.get_data()
        players_count = len(game_data["players_ids"])
        if not game_data[Mafia.roles_key]:
            if not game_data.get(Killer.roles_key):
                raise GameIsOver(winner=Groupings.civilians)
            killers_count = len(game_data.get(Killer.roles_key))
            if killers_count >= players_count - killers_count:
                raise GameIsOver(winner=Groupings.killer)
        criminals_count = 0
        for role in self.all_roles:
            current_role: Role = self.all_roles[role]
            if current_role.grouping == Groupings.criminals:
                if current_role.is_alias:
                    continue
                criminals_count += len(
                    game_data[current_role.roles_key]
                )
        if (
            criminals_count > players_count - criminals_count
        ):  # TODO >=
            raise GameIsOver(winner=Groupings.criminals)
        return result

    return wrapper


class Executor:
    def __init__(
        self,
        message: Message,
        state: FSMContext,
        dispatcher: Dispatcher,
        scheduler: AsyncIOScheduler,
        mailer: MailerToPlayers,
    ):

        self.message = message
        self.state = state
        self.dispatcher = dispatcher
        self.scheduler = scheduler
        self.bot = message.bot
        self.group_chat_id = self.message.chat.id
        self.mailer = mailer
        self.all_roles = {}

    async def clear_data_after_all_actions(self):
        game_data: GameCache = await self.state.get_data()
        for role in self.all_roles:
            current_role: Role = self.all_roles[role]
            if (
                current_role.alias
                and current_role.alias.is_mass_mailing_list
                and current_role.last_interactive_key
            ):
                current_night = game_data["number_of_night"]
                processed_user_id = (
                    current_role.get_processed_user_id(game_data)
                )
                if processed_user_id:
                    last_interactive: LastInteraction = game_data[
                        current_role.last_interactive_key
                    ]
                    excess_players = [
                        user_id_str
                        for user_id_str, nights in last_interactive.items()
                        if nights
                        and nights[-1] == current_night
                        and str(processed_user_id) != user_id_str
                    ]
                    for user_id_str in excess_players:
                        last_interactive[user_id_str].pop()

            if current_role.processed_users_key in game_data:
                game_data[current_role.processed_users_key].clear()
            if current_role.processed_by_boss:
                game_data[current_role.processed_by_boss].clear()
            if current_role.extra_data:
                for extra in current_role.extra_data:
                    if extra.is_cleared and extra.key in game_data:
                        game_data[extra.key].clear()
        game_data["pros"].clear()
        game_data["cons"].clear()
        game_data["vote_for"].clear()
        game_data["messages_after_night"].clear()
        await self.state.set_data(game_data)

    def get_voting_roles(self):
        return [
            self.all_roles[role]
            for role in self.all_roles
            if isinstance(self.all_roles[role], VictimsOfVote)
            and self.all_roles[role].is_alias is False
        ]

    @check_end_of_game
    async def sum_up_after_voting(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        pros = game_data["pros"]
        cons = game_data["cons"]
        removed_user_id = get_the_most_frequently_encountered_id(
            [voted for _, voted in game_data["vote_for"]]
        )
        result_text = get_results_of_voting(
            game_data=game_data, removed_user_id=removed_user_id
        )
        voting_roles = self.get_voting_roles()
        voting_roles.sort(
            key=attrgetter("number_in_order_after_voting")
        )
        kwargs = {
            "all_roles": self.all_roles,
            "game_data": game_data,
        }
        is_not_there_removed = len(pros) == len(cons) or len(
            pros
        ) < len(cons)
        if is_not_there_removed:
            removed_user = [0]
        else:
            removed_user = [removed_user_id]
        for role in voting_roles:
            await role.take_action_after_voting(
                **kwargs,
                removed_user=removed_user,
            )
        if removed_user_id is None or is_not_there_removed:
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text=result_text,
            )
            return
        if removed_user_id != removed_user[0]:
            return
        user_info: UserGameCache = game_data["players"][
            str(removed_user_id)
        ]
        for user_id in set(pros):
            current_role = self.all_roles[
                game_data["players"][str(user_id)]["enum_name"]
            ]
            current_role.earn_money_for_voting(
                voted_role=self.all_roles[user_info["enum_name"]],
                voted_user=user_info,
                game_data=game_data,
                user_id=user_id,
            )
        await self.remove_user_from_game(
            game_data=game_data,
            user_id=removed_user_id,
            is_night=False,
        )
        await self.bot.send_message(
            chat_id=game_data["game_chat"],
            text=result_text
            + f"Сегодня народ принял тяжелое решение и повесил "
            f'{user_info["url"]} с ролью {user_info["pretty_role"]}!',
        )
        await self.state.set_data(game_data)

    @check_end_of_game
    async def sum_up_after_night(self):
        game_data: GameCache = await self.state.get_data()
        roles: list[ProcedureAfterNight] = [
            self.all_roles[role]
            for role in self.all_roles
            if isinstance(self.all_roles[role], ProcedureAfterNight)
            and self.all_roles[role].is_alias is False
        ]
        roles.sort(key=attrgetter("number_in_order_after_night"))
        victims = set()
        recovered = []
        murdered = []
        kwargs = {
            "recovered": recovered,
            "murdered": murdered,
            "victims": victims,
            "game_data": game_data,
            "all_roles": self.all_roles,
        }
        for role in roles:
            await role.procedure_after_night(**kwargs)
        victims |= set(murdered) - set(recovered)
        for role in roles:
            await role.accrual_of_overnight_rewards(**kwargs)

        text_about_dead = ""
        for victim_id in victims:
            await self.remove_user_from_game(
                game_data=game_data, user_id=victim_id, is_night=True
            )
            url = game_data["players"][str(victim_id)]["url"]
            role = game_data["players"][str(victim_id)][
                "pretty_role"
            ]
            text_about_dead += f"Убит {role} - {url}!\n\n"

        text_about_dead = (
            text_about_dead or "Сегодня ночью все выжили!"
        )
        await self.bot.send_message(
            chat_id=self.group_chat_id, text=text_about_dead
        )
        await self.mailer.send_messages_after_night(
            game_data=game_data
        )
        await self.state.set_data(game_data)

    async def confirm_final_aim(
        self,
    ) -> bool:
        game_data: GameCache = await self.state.get_data()
        vote_for = game_data["vote_for"]
        aim_id = get_the_most_frequently_encountered_id(
            [voted for _, voted in vote_for]
        )
        text = get_results_of_goal_identification(
            game_data=game_data
        )
        await self.bot.send_message(
            chat_id=self.group_chat_id,
            text=text,
        )
        if aim_id is None:
            return False
        url = game_data["players"][str(aim_id)]["url"]
        await self.state.set_state(GameFsm.VOTE)
        sent_survey = await self.bot.send_message(
            chat_id=self.group_chat_id,
            text=f"На кону судьба {url}!",
            reply_markup=get_vote_for_aim_kb(
                user_id=aim_id,
                pros=game_data["pros"],
                cons=game_data["cons"],
            ),
        )
        game_data["to_delete"].append(
            [self.group_chat_id, sent_survey.message_id]
        )
        return True

    async def delete_message_by_chat(
        self, chat_id: int, message_id: int
    ):
        with suppress(TelegramBadRequest):
            await self.bot.delete_message(
                chat_id=chat_id, message_id=message_id
            )

    async def delete_messages_from_to_delete(
        self, to_delete: ChatsAndMessagesIds
    ):
        await asyncio.gather(
            *(
                self.delete_message_by_chat(
                    chat_id=chat_id,
                    message_id=message_id,
                )
                for chat_id, message_id in to_delete
            )
        )

    async def remove_user_from_game(
        self, game_data: GameCache, user_id: int, is_night: bool
    ):
        if is_night:
            await get_state_and_assign(
                dispatcher=self.dispatcher,
                chat_id=user_id,
                bot_id=self.bot.id,
                new_state=UserFsm.WAIT_FOR_LATEST_LETTER,
            )
        user_role = game_data["players"][str(user_id)]["enum_name"]
        role: Role = self.all_roles[user_role]
        await role.report_death(
            game_data=game_data, is_night=is_night, user_id=user_id
        )
        game_data["players_ids"].remove(user_id)
        game_data["players"][str(user_id)][
            "number_died_at_night"
        ] = (game_data["number_of_night"] - 1)
        game_data[role.roles_key].remove(user_id)
        if (
            isinstance(role, BossIsDeadMixin)
            and role.is_alias is False
        ):
            await role.boss_is_dead(current_id=user_id)
        if isinstance(role, AliasRole):
            await role.alias_is_dead(
                current_id=user_id, game_data=game_data
            )
