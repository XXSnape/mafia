from general.collection_of_roles import get_data_with_roles
from general.groupings import Groupings
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from mafia.roles import Hacker
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_state_and_data,
    get_game_state_data_and_user_id,
)
from utils.common import get_criminals_ids
from utils.informing import send_a_lot_of_messages_safely
from utils.pretty_text import make_build
from utils.tg import delete_message


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
            text=f"По слухам, {role} {url} перед смертью "
            f"проглаголил такие слова:\n\n{self.message.text}"[
                :3900
            ],
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
        current_role = get_data_with_roles(
            game_data["players"][str(self.message.from_user.id)][
                "role_id"
            ]
        )
        criminals_ids = get_criminals_ids(game_data)
        if current_role.grouping == Groupings.criminals:
            aliases = criminals_ids
        else:
            aliases = game_data[current_role.roles_key]
        if len(aliases) == 1:
            return
        await send_a_lot_of_messages_safely(
            bot=self.message.bot,
            users=aliases,
            text=f"{role} {url} передает:\n\n{self.message.text}"[
                :3900
            ],
            exclude=[self.message.from_user.id],
        )
        if (
            self.message.from_user.id in criminals_ids
            and game_data.get(Hacker.roles_key)
        ):
            await send_a_lot_of_messages_safely(
                bot=self.message.bot,
                text=f"{role} ??? передает:\n\n{self.message.text}"[
                    :3900
                ],
                users=game_data[Hacker.roles_key],
            )
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
        deceived_user = game_data.get("deceived", [])
        if (
            len(deceived_user) == 2
            and self.callback.from_user.id == deceived_user[0]
            and deceived_user[1] in game_data["live_players_ids"]
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
