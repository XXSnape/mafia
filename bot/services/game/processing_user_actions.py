import asyncio

from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from services.base import RouterHelper
from services.game.actions_at_night import (
    get_game_state_and_data,
    get_game_state_data_and_user_id,
)
from services.game.roles import Hacker, Mafia
from utils.tg import delete_message
from utils.pretty_text import make_build


class UserManager(RouterHelper):
    async def send_latest_message(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.message,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        role = game_data["players"][str(self.message.from_user.id)][
            "pretty_role"
        ]
        url = game_data["players"][str(self.message.from_user.id)][
            "url"
        ]
        await self.message.bot.send_message(
            chat_id=game_data["game_chat"],
            text=f"По слухам {role} {url} перед смертью проглаголил такие слова:\n\n{self.message.text}",
        )
        await self.message.answer(
            make_build("Сообщение успешно отправлено!")
        )
        await self.state.clear()

    async def allies_communicate(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.message,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        url = game_data["players"][str(self.message.from_user.id)][
            "url"
        ]
        role = game_data["players"][str(self.message.from_user.id)][
            "pretty_role"
        ]
        aliases = game_data["players"][
            str(self.message.from_user.id)
        ]["roles_key"]
        await asyncio.gather(
            *(
                self.message.bot.send_message(
                    chat_id=player_id,
                    text=f"{role} {url} передает:\n\n{self.message.text}",
                )
                for player_id in game_data[aliases]
                if player_id != self.message.from_user.id
            ),
            return_exceptions=True,
        )
        if self.message.from_user.id in game_data[
            Mafia.roles_key
        ] and game_data.get(Hacker.roles_key):
            await asyncio.gather(
                *(
                    self.message.bot.send_message(
                        chat_id=hacker_id,
                        text=f"{role} ??? передает:\n\n{self.message.text}",
                    )
                    for hacker_id in game_data[Hacker.roles_key]
                ),
                return_exceptions=True,
            )
        if len(game_data[aliases]) > 1:
            await self.message.answer(
                make_build("Сообщение успешно отправлено!")
            )

    async def vote_for(self, callback_data: UserActionIndexCbData):
        game_state, game_data, voted_user_id = (
            await get_game_state_data_and_user_id(
                callback=self.callback,
                callback_data=callback_data,
                state=self.state,
                dispatcher=self.dispatcher,
            )
        )
        deceived_user = game_data.get("deceived")
        if (
            deceived_user
            and self.callback.from_user.id == deceived_user[0]
        ):
            voted_user_id = deceived_user[1]
        game_data["vote_for"].append(
            [self.callback.from_user.id, voted_user_id]
        )
        voting_url = game_data["players"][
            str(self.callback.from_user.id)
        ]["url"]
        voted_url = game_data["players"][str(voted_user_id)]["url"]
        await delete_message(self.callback.message)
        await game_state.set_data(game_data)
        await self.callback.message.answer(
            make_build(f"Ты выбрал голосовать за {voted_url}")
        )
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(
                f"❗️{voting_url} выступает против {voted_url}!"
            ),
            reply_markup=participate_in_social_life(),
        )
