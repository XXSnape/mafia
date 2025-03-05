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
    Roles,
    Role,
    PlayersIds,
    RolesKeysLiteral,
)
from general.players import Groupings
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
        game_data["vote_for"].clear()
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
        for role in Roles:
            current_role: Role = role.value
            if (
                current_role.processed_users_key
                and current_role.processed_users_key in game_data
            ):
                game_data[current_role.processed_users_key].clear()
            if current_role.extra_data:
                for extra in current_role.extra_data:
                    if extra.is_cleared and extra.key in game_data:
                        game_data[extra.key].clear()
        await self.state.set_data(game_data)

    async def check_analyst_win(
        self,
        analyst_id: int | None,
        removed_user: list[int],
        game_data: GameCache,
    ):
        if not analyst_id:
            return
        if game_data["predicted"] == removed_user:
            await self.bot.send_message(
                chat_id=analyst_id, text="Прекрасная дедукция!"
            )
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="Все, кто читал прогнозы на день, были готовы к дневным событиям!",
            )
        else:
            await self.bot.send_message(
                chat_id=analyst_id, text="Сегодня интуиция подвела!"
            )
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text="Обман или чёрный лебедь? Аналитические прогнозы не сбылись!",
            )

    @check_end_of_game
    async def sum_up_after_voting(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        pros = game_data["pros"]
        cons = game_data["cons"]
        analysts = game_data.get("analysts")
        analyst = None if not analysts else analysts[0]
        if len(pros) == len(cons) or len(pros) < len(cons):
            await self.check_analyst_win(
                analyst_id=analyst,
                removed_user=[0],
                game_data=game_data,
            )
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text=f"Что ж, такова воля народа! Сегодня днем город не опустел!",
            )
            return

        removed_user = game_data["vote_for"][0]
        user_info: UserGameCache = game_data["players"][
            str(removed_user)
        ]

        if removed_user in game_data["have_alibi"]:
            await self.check_analyst_win(
                analyst_id=analyst,
                removed_user=[0],
                game_data=game_data,
            )
            await self.bot.send_message(
                chat_id=game_data["game_chat"],
                text=f"У {user_info['url']} есть алиби, поэтому местные жители отпустили гвоздя программы",
            )
            return
        await self.check_analyst_win(
            analyst_id=analyst,
            removed_user=[removed_user],
            game_data=game_data,
        )
        if removed_user in game_data["angels_of_death"]:
            game_data["angels_died"].append(removed_user)
        self.remove_user_from_game(
            game_data=game_data, user_id=removed_user, is_night=False
        )
        await self.bot.send_message(
            chat_id=game_data["game_chat"],
            text=f'Сегодня народ принял тяжелое решение и повесил {user_info["url"]} с ролью {user_info["pretty_role"]}!',
        )

    @staticmethod
    def get_first_persons(
        *keys: RolesKeysLiteral, gema_data: GameCache
    ):
        ids = []
        for key in keys:
            if key in gema_data and gema_data[key]:
                ids.append(gema_data[key][0])
        return ids

    async def revenge_of_punisher(
        self, game_data: GameCache, victims: set
    ):
        punishers = game_data.get("punishers")
        if not punishers:
            return
        punisher_id = punishers[0]
        killed_py_punisher = set()
        if punisher_id not in victims:
            return
        for role in Roles:
            current_role: Role = role.value
            if (
                current_role.can_kill_at_night_and_survive is False
                or current_role.processed_users_key is None
            ):
                continue
            if punisher_id in game_data.get(
                current_role.processed_users_key, []
            ):
                player_id = game_data[current_role.roles_key][0]
                killed_py_punisher.add(player_id)
        await self.bot.send_message(
            chat_id=punisher_id,
            text="Все нарушители твоего покоя будут наказаны!",
        )
        victims |= killed_py_punisher

    @check_end_of_game
    async def sum_up_after_night(self):
        game_data: GameCache = await self.state.get_data()
        victims = (
            set(game_data["killed_by_mafia"])
            | set(game_data["killed_by_angel_of_death"])
        ) - (
            set(game_data["treated_by_doctor"])
            | set(game_data["treated_by_bodyguard"])
        )
        await self.revenge_of_punisher(
            game_data=game_data, victims=victims
        )
        bombers = game_data.get("suicide_bombers", [])[:]

        if game_data["treated_by_bodyguard"]:
            if (
                game_data["bodyguards"][0]
                not in game_data["treated_by_doctor"]
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
                        chat_id=victim_id, bombers=bombers
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
        roles = {}
        for role in Roles:
            current_role: Role = role.value
            roles[current_role.role] = game_data[
                current_role.roles_key
            ]
        user_role = game_data["players"][str(user_id)]["role"]
        roles[user_role].remove(user_id)
