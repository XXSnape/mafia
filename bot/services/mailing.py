import asyncio
from collections.abc import Iterable
from typing import Literal

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from cache.cache_types import (
    GameCache,
    RolesKeysLiteral,
    LivePlayersIds,
    UsersInGame,
)
from keyboards.inline.callback_factory.user_index import (
    UserVoteIndexCbData,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from keyboards.inline.keypads.to_bot import get_to_bot_kb
from services.registartion import get_state_and_assign
from states.states import UserFsm


async def familiarize_players(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    mafias = game_data["mafias"]
    doctors = game_data["doctors"]
    policeman = game_data["policeman"]
    civilians = game_data["civilians"]

    for user_id in mafias:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Мафия! Тебе нужно уничтожить всех горожан.",
        )
    for user_id in doctors:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Доктор! Тебе нужно стараться лечить тех, кому нужна помощь.",
        )
    for user_id in policeman:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Комиссар! Тебе нужно вычислить мафию.",
        )
    for user_id in civilians:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Мирный житель! Тебе нужно вычислить мафию на голосовании.",
        )


class MailerToPlayers:
    def __init__(
        self,
        state: FSMContext,
        bot: Bot,
        dispatcher: Dispatcher,
        group_chat_id: int,
    ):
        self.state = state
        self.bot = bot
        self.dispatcher = dispatcher
        self.group_chat_id = group_chat_id

    async def _mail_user(
        self,
        text: str,
        role_key: RolesKeysLiteral,
        new_state: State,
        exclude: Iterable[int] | int = (),
    ):
        game_data: GameCache = await self.state.get_data()
        roles = game_data[role_key]
        role_id = roles[0]
        players = game_data["players"]
        markup = send_selection_to_players_kb(
            players_ids=game_data["players_ids"],
            players=players,
            exclude=exclude,
        )
        sent_survey = await self.bot.send_message(
            chat_id=role_id,
            text=text,
            reply_markup=markup,
        )
        game_data["to_delete"].append(sent_survey.message_id)
        await self.state.set_data(game_data)
        await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=role_id,
            bot_id=self.bot.id,
            new_state=new_state,
        )

    async def mail_mafia(self):
        game_data: GameCache = await self.state.get_data()
        mafias = game_data["mafias"]
        mafia_id = mafias[0]
        await self._mail_user(
            text="Кого убить этой ночью?",
            role_key="mafias",
            new_state=UserFsm.MAFIA_ATTACKS,
            exclude=mafia_id,
        )

    async def mail_doctor(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        exclude = (
            []
            if game_data["last_treated"] == 0
            else game_data["last_treated"]
        )
        await self._mail_user(
            text="Кого вылечить этой ночью?",
            role_key="doctors",
            new_state=UserFsm.DOCTOR_TREATS,
            exclude=exclude,
        )

    async def mail_policeman(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        exclude = game_data["policeman"]
        await self._mail_user(
            text="Кого проверить этой ночью?",
            role_key="policeman",
            new_state=UserFsm.POLICEMAN_CHECKS,
            exclude=exclude,
        )

    async def send_request_to_vote(
        self,
        user_id: int,
        players_ids: LivePlayersIds,
        players: UsersInGame,
    ):
        await self.bot.send_message(
            chat_id=user_id,
            text="Проголосуй за того, кто не нравится!",
            reply_markup=send_selection_to_players_kb(
                players_ids=players_ids,
                players=players,
                exclude=user_id,
                user_index_cb=UserVoteIndexCbData,
            ),
        )

    async def suggest_vote(self):
        await self.bot.send_message(
            chat_id=self.group_chat_id,
            text="Кого обвиним во всем и повесим?",
            reply_markup=get_to_bot_kb(
                text="Участвовать в социальной жизни!"
            ),
        )
        game_data: GameCache = await self.state.get_data()
        live_players = game_data["players_ids"]
        players = game_data["players"]
        await asyncio.gather(
            *(
                self.send_request_to_vote(
                    user_id=user_id,
                    players_ids=live_players,
                    players=players,
                )
                for user_id in live_players
            )
        )
