from contextlib import suppress
from datetime import timedelta

from aiogram.exceptions import TelegramAPIError
from cache.cache_types import GameCache, PlayersIds
from keyboards.inline.callback_factory.recognize_user import (
    AimedUserCbData,
    ProsAndCons,
)
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from mafia.roles import PrimeMinister
from services.base import RouterHelper
from utils.informing import get_profiles
from utils.pretty_text import make_build
from utils.state import lock_state
from utils.tg import ban_user, delete_message, resending_message


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
            (
                self.message.from_user.id
                not in game_data["live_players_ids"]
            )
            or self.message.from_user.id in game_data["cant_talk"]
            or (
                game_data["settings"]["can_talk_at_night"] is False
                and game_data["at_night"]
            )
        ):
            await delete_message(message=self.message)
            await ban_user(
                bot=self.message.bot,
                chat_id=game_data["game_chat"],
                user_id=self.message.from_user.id,
                until_date=timedelta(seconds=30),
            )

    async def confirm_vote(self, callback_data: AimedUserCbData):
        async with lock_state(self.state):
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
                    "🚫Теперь твой судья — демократия!",
                    show_alert=True,
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
            await self.state.set_data(game_data)
            with suppress(TelegramAPIError, AttributeError):
                await self.callback.message.edit_reply_markup(
                    reply_markup=get_vote_for_aim_kb(
                        user_id=callback_data.user_id,
                        pros=game_data["pros"],
                        cons=game_data["cons"],
                    )
                )
        await self.callback.answer(
            text="✅Твое мнение учтено",
            show_alert=True,
        )

    async def want_to_exit_game(self):
        await delete_message(message=self.message)
        user_id = self.message.from_user.id
        async with lock_state(self.state):
            game_data: GameCache = await self.state.get_data()
            if user_id not in game_data["live_players_ids"]:
                await ban_user(
                    bot=self.message.bot,
                    chat_id=game_data["game_chat"],
                    user_id=user_id,
                    until_date=timedelta(seconds=30),
                )
                return
            if user_id in game_data["wish_to_leave_game"]:
                return
            game_data["wish_to_leave_game"] = [
                wish_to_leave_id
                for wish_to_leave_id in game_data[
                    "wish_to_leave_game"
                ]
                if wish_to_leave_id in game_data["live_players_ids"]
            ] + [user_id]
            await self.state.set_data(game_data)
        users = get_profiles(
            players_ids=game_data["wish_to_leave_game"],
            players=game_data["players"],
            sorting_factory=None,
        )
        number_of_people_to_leave = len(
            game_data["wish_to_leave_game"]
        )
        total_number_of_players = len(game_data["live_players_ids"])
        text = (
            f"❗️Игроки, желающие завершить игру досрочно "
            f"({number_of_people_to_leave} из {total_number_of_players}):\n{users}"
        )
        if number_of_people_to_leave == total_number_of_players:
            text += "\n\n🏁Игра скоро завершится"
        await resending_message(
            bot=self.message.bot,
            chat_id=self.message.chat.id,
            text=make_build(text),
        )
