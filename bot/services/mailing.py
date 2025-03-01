from collections.abc import Iterable
from typing import Literal

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from cache.cache_types import GameCache, RolesKeysLiteral
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
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
        self, state: FSMContext, bot: Bot, dispatcher: Dispatcher
    ):
        self.state = state
        self.bot = bot
        self.dispatcher = dispatcher

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
