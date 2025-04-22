from contextlib import suppress
from datetime import timedelta

from aiogram.exceptions import TelegramBadRequest
from cache.cache_types import GameCache, PlayersIds
from keyboards.inline.callback_factory.recognize_user import (
    AimedUserCbData,
    ProsAndCons,
)
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from mafia.roles import PrimeMinister
from services.base import RouterHelper
from utils.tg import ban_user, delete_message


class GroupManager(RouterHelper):
    @staticmethod
    def _add_voice(
        user_id: int,
        add_to: PlayersIds,
        delete_from: PlayersIds,
        prime_ministers: PlayersIds,
    ):
        repeat = 2 if user_id in prime_ministers else 1
        for _ in range(repeat):
            with suppress(ValueError):
                delete_from.remove(user_id)
        if user_id not in add_to:
            for _ in range(repeat):
                add_to.append(user_id)

    async def delete_message_from_non_players(self):
        game_data: GameCache = await self.state.get_data()
        if (
            self.message.from_user.id
            not in game_data["live_players_ids"]
        ) or self.message.from_user.id in game_data["cant_talk"]:
            await delete_message(message=self.message)
            await ban_user(
                bot=self.message.bot,
                chat_id=game_data["game_chat"],
                user_id=self.message.from_user.id,
                until_date=timedelta(seconds=30),
            )

    async def confirm_vote(self, callback_data: AimedUserCbData):
        game_data: GameCache = await self.state.get_data()
        if (
            self.callback.from_user.id
            not in game_data["live_players_ids"]
        ):
            await self.callback.answer(
                "🚫Ты не в игре!", show_alert=True
            )
            return

        if callback_data.user_id == self.callback.from_user.id:
            await self.callback.answer(
                "🚫Теперь твой судья - демократия!", show_alert=True
            )
            return
        if self.callback.from_user.id in game_data["cant_vote"]:
            await self.callback.answer(
                "🚫Ты временно не можешь голосовать!",
                show_alert=True,
            )
            return
        if callback_data.action == ProsAndCons.pros:
            self._add_voice(
                user_id=self.callback.from_user.id,
                add_to=game_data["pros"],
                delete_from=game_data["cons"],
                prime_ministers=game_data.get(
                    PrimeMinister.roles_key, []
                ),
            )
        elif callback_data.action == ProsAndCons.cons:
            self._add_voice(
                user_id=self.callback.from_user.id,
                add_to=game_data["cons"],
                delete_from=game_data["pros"],
                prime_ministers=game_data.get(
                    PrimeMinister.roles_key, []
                ),
            )
        with suppress(TelegramBadRequest, AttributeError):
            await self.callback.message.edit_reply_markup(
                reply_markup=get_vote_for_aim_kb(
                    user_id=callback_data.user_id,
                    pros=game_data["pros"],
                    cons=game_data["cons"],
                )
            )
        await self.state.set_data(game_data)
        await self.callback.answer(
            text="✅Мы обязательно учтём твое мнение",
            show_alert=True,
        )
