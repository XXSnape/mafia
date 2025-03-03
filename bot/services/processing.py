import asyncio
from collections.abc import Callable
from contextlib import suppress
from random import randint
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatPermissions
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cache.cache_types import (
    GameCache,
    UserGameCache,
    ChatsAndMessagesIds,
)
from general.players import Groupings, Roles
from general.exceptions import GameIsOver
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from services.mailing import MailerToPlayers
from states.states import GameFsm
from utils.utils import get_profiles

if TYPE_CHECKING:
    from .pipeline_game import Game


def check_end_of_game(async_func: Callable):
    async def wrapper(self: "Game"):
        result = await async_func(self)
        state = self.state
        game_data: GameCache = await state.get_data()
        if not game_data["mafias"]:
            raise GameIsOver(winner=Groupings.civilians)
        if len(game_data["players_ids"]) == 2:
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

    async def clear_data_after_all_actions(self):
        game_data: GameCache = await self.state.get_data()
        game_data["pros"].clear()
        game_data["cons"].clear()
        game_data["recovered"].clear()
        game_data["vote_for"].clear()
        game_data["died"].clear()
        game_data["protected"].clear()
        game_data["self_protected"].clear()
        game_data["have_alibi"].clear()
        for cant_vote_id in game_data["cant_vote"]:
            with suppress(TelegramBadRequest):
                await self.bot.restrict_chat_member(
                    chat_id=self.group_chat_id,
                    user_id=cant_vote_id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_other_messages=True,
                        can_send_polls=True,
                    ),
                )
        game_data["cant_vote"].clear()
        await self.state.set_data(game_data)

    @check_end_of_game
    async def sum_up_after_voting(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        pros = game_data["pros"]
        cons = game_data["cons"]
        if len(pros) == len(cons) or len(pros) < len(cons):
            await self.bot.send_message(
                chat_id=game_data["game_chat"],
                text=f"Что ж, такова воля народа! Сегодня днем город не опустел!",
            )
            return
        removed_user = game_data["vote_for"][0]
        user_info: UserGameCache = game_data["players"][
            str(removed_user)
        ]

        if removed_user in game_data["have_alibi"]:
            await self.bot.send_message(
                chat_id=game_data["game_chat"],
                text=f"У {user_info['url']} есть алиби, поэтому местные жители отпустили гвоздя программы",
            )
            return
        self.remove_user_from_game(
            game_data=game_data, user_id=removed_user, is_night=False
        )
        await self.bot.send_message(
            chat_id=game_data["game_chat"],
            text=f'Сегодня народ принял тяжелое решение и повесил {user_info["url"]} с ролью {user_info["pretty_role"]}!',
        )

    @check_end_of_game
    async def sum_up_after_night(self):
        game_data: GameCache = await self.state.get_data()
        victims = (
            set(game_data["died"])
            - set(game_data["recovered"])
            - set(game_data["self_protected"])
        )
        if game_data["self_protected"]:
            if (
                game_data["bodyguards"][0]
                not in game_data["recovered"]
            ):
                victims.add(game_data["bodyguards"][0])
        text_about_dead = ""
        for victim_id in victims:
            if victim_id in game_data["lucky_guys"]:
                if randint(1, 10) in (1, 2, 3, 4):
                    await self.bot.send_message(
                        chat_id=victim_id,
                        text="Тебе сегодня крупно повезло!",
                    )
                    victims.remove(victim_id)
                    continue
            self.remove_user_from_game(
                game_data=game_data, user_id=victim_id, is_night=True
            )
            url = game_data["players"][str(victim_id)]["url"]
            role = game_data["players"][str(victim_id)][
                "pretty_role"
            ]
            text_about_dead += (
                f"Сегодня был убит {role} - {url}!\n\n"
            )

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
        if victims:
            await asyncio.gather(
                *(
                    self.mailer.report_death(
                        chat_id=victim_id,
                    )
                    for victim_id in victims
                )
            )

    async def confirm_final_aim(
        self,
    ) -> bool:
        game_data: GameCache = await self.state.get_data()
        vote_for = game_data["vote_for"]
        vote_for.sort(reverse=True)

        if (not vote_for) or (
            len(vote_for) != 1
            and vote_for.count(vote_for[0])
            == vote_for.count(vote_for[1])
        ):
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="Доброта или банальная несогласованность? "
                "Посмотрим, воспользуются ли преступники таким подарком.",
            )
            return False
        aim_id = vote_for[0]
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

    @staticmethod
    def remove_user_from_game(
        game_data: GameCache, user_id: int, is_night: bool
    ):
        if user_id in game_data["masochists"]:
            if is_night:
                game_data["losers"].append(user_id)
            else:
                game_data["winners"].append(user_id)
        if user_id in game_data["suicide_bombers"]:
            if is_night:
                game_data["winners"].append(user_id)
            else:
                game_data["losers"].append(user_id)
        game_data["players_ids"].remove(user_id)
        roles = {
            Roles.mafia: game_data["mafias"],
            Roles.doctor: game_data["doctors"],
            Roles.policeman: game_data["policeman"],
            Roles.civilian: game_data["civilians"],
            Roles.lawyer: game_data["lawyers"],
            Roles.masochist: game_data["masochists"],
            Roles.prosecutor: game_data["prosecutors"],
            Roles.lucky_gay: game_data["lucky_guys"],
            Roles.suicide_bomber: game_data["suicide_bombers"],
            Roles.bodyguard: game_data["bodyguards"],
        }
        user_role = game_data["players"][str(user_id)]["role"]
        roles[user_role].remove(user_id)
