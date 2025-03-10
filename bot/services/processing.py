import asyncio
from collections.abc import Callable
from contextlib import suppress
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
)
from general.exceptions import GameIsOver
from general.players import Groupings
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from services.mailing import MailerToPlayers
from states.states import GameFsm, UserFsm
from utils.utils import (
    get_profiles,
    get_state_and_assign,
    get_the_most_frequently_encountered_id,
)

from .protocols.protocols import (
    DelayedMessagesAfterNight,
    EarliestActionsAfterNight,
    ModificationVictims,
    VictimsOfVote,
)
from .roles import Lawyer
from .roles.base import AliasRole, BossIsDeadMixin, Role
from .roles.base.mixins import TreatmentMixin

if TYPE_CHECKING:
    from .pipeline_game import Game


def check_end_of_game(async_func: Callable):
    async def wrapper(self: "Game"):
        result = await async_func(self)
        state = self.state
        game_data: GameCache = await state.get_data()
        if not game_data["mafias"]:
            raise GameIsOver(winner=Groupings.civilians)

        if len(game_data["mafias"]) > (  # TODO <=
            len(game_data["players_ids"]) - len(game_data["mafias"])
        ):
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
                    last_interactive = game_data[
                        current_role.last_interactive_key
                    ]
                    excess_players = [
                        user_id_str
                        for user_id_str, night in last_interactive.items()
                        if night == current_night
                        and str(processed_user_id) != user_id_str
                    ]
                    for user_id_str in excess_players:
                        last_interactive.pop(user_id_str)

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
        await self.state.set_data(game_data)

    async def start_earliest_actions(self):
        for role in self.all_roles:
            current_role = self.all_roles[role]
            if isinstance(current_role, EarliestActionsAfterNight):
                await current_role.earliest_actions_after_night(
                    all_roles=self.all_roles
                )

    async def send_promised_messages(self, game_data: GameCache):
        for role in self.all_roles:
            current_role = self.all_roles[role]
            if isinstance(current_role, DelayedMessagesAfterNight):
                await current_role.send_delayed_messages_after_night(
                    game_data=game_data
                )

    def get_voting_roles(self):
        return [
            self.all_roles[role]
            for role in self.all_roles
            if isinstance(self.all_roles[role], VictimsOfVote)
        ]

    @check_end_of_game
    async def sum_up_after_voting(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        pros = game_data["pros"]
        cons = game_data["cons"]
        voting_roles = self.get_voting_roles()
        if len(pros) == len(cons) or len(pros) < len(cons):
            for role in voting_roles:
                await role.take_action_after_voting(
                    game_data=game_data,
                    user_id=0,
                )
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text=f"Что ж, такова воля народа! Сегодня днем город не опустел!",
            )
            return
        removed_user_id = get_the_most_frequently_encountered_id(
            game_data["vote_for"]
        )
        user_info: UserGameCache = game_data["players"][
            str(removed_user_id)
        ]
        if removed_user_id == Lawyer().get_processed_user_id(
            game_data
        ):
            for role in voting_roles:
                await role.take_action_after_voting(
                    game_data=game_data,
                    user_id=0,
                )
            await self.bot.send_message(
                chat_id=game_data["game_chat"],
                text=f"У {user_info['url']} есть алиби, поэтому местные жители отпустили гвоздя программы",
            )
            return
        for role in voting_roles:
            await role.take_action_after_voting(
                game_data=game_data,
                user_id=removed_user_id,
            )
        await self.remove_user_from_game(
            game_data=game_data,
            user_id=removed_user_id,
            is_night=False,
        )
        await self.bot.send_message(
            chat_id=game_data["game_chat"],
            text=f'Сегодня народ принял тяжелое решение и повесил {user_info["url"]} с ролью {user_info["pretty_role"]}!',
        )

    @check_end_of_game
    async def sum_up_after_night(self):
        game_data: GameCache = await self.state.get_data()
        attacking_roles = [
            self.all_roles[role]
            for role in self.all_roles
            if self.all_roles[role].can_kill_at_night
        ]
        murdered = []
        for role in attacking_roles:
            user_id = role.get_processed_user_id(game_data)
            if user_id:
                murdered.append(user_id)
        recovered = []

        healing_roles = [
            self.all_roles[role]
            for role in self.all_roles
            if isinstance(self.all_roles[role], TreatmentMixin)
        ]
        healing_roles.sort()
        for heal_role in healing_roles:
            heal_role: TreatmentMixin
            heal_role.treat(
                game_data=game_data,
                recovered=recovered,
                murdered=murdered,
            )
        victims = set(murdered) - set(recovered)
        for role in self.all_roles:
            current_role = self.all_roles[role]
            if isinstance(current_role, ModificationVictims):
                await current_role.change_victims(
                    game_data=game_data,
                    attacking_roles=attacking_roles,
                    victims=victims,
                    recovered=recovered,
                )

        text_about_dead = ""
        for victim_id in victims:
            await self.remove_user_from_game(
                game_data=game_data, user_id=victim_id, is_night=True
            )
            url = game_data["players"][str(victim_id)]["url"]
            role = game_data["players"][str(victim_id)][
                "pretty_role"
            ]
            text_about_dead += f"Ночью был убит {role} - {url}!\n\n"

        live_players = get_profiles(
            live_players_ids=game_data["players_ids"],
            players=game_data["players"],
        )
        text_about_dead = (
            text_about_dead or "Сегодня ночью все выжили!"
        )
        await self.bot.send_message(
            chat_id=self.group_chat_id, text=text_about_dead
        )
        await self.bot.send_photo(
            chat_id=self.group_chat_id,
            photo="https://i.pinimg.com/originals/b1/80/98/b18098074864e4b1bf5cc8412ced6421.jpg",
            caption="Живые игроки:\n" + live_players,
        )

    async def confirm_final_aim(
        self,
    ) -> bool:
        game_data: GameCache = await self.state.get_data()
        vote_for = game_data["vote_for"]
        aim_id = get_the_most_frequently_encountered_id(vote_for)
        if aim_id is None:
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="Доброта или банальная несогласованность? "
                "Посмотрим, воспользуются ли преступники таким подарком.",
            )
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
        role = self.all_roles[user_role]
        await role.report_death(
            game_data=game_data, is_night=is_night, user_id=user_id
        )
        game_data["players_ids"].remove(user_id)
        game_data["players"][str(user_id)][
            "number_died_at_night"
        ] = game_data["number_of_night"]
        game_data[role.roles_key].remove(user_id)
        if isinstance(role, BossIsDeadMixin):
            await role.boss_is_dead(current_id=user_id)
        if isinstance(role, AliasRole):
            await role.alias_is_dead(
                current_id=user_id, game_data=game_data
            )
