from typing import cast

from cache.cache_types import GameCache, RolesLiteral
from general.collection_of_roles import get_data_with_roles
from general.text import NUMBER_OF_NIGHT
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.mailing import choose_fake_role_kb
from mafia.roles import Forger
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_data_and_user_id,
    get_game_state_by_user_state,
    send_messages_to_user_and_group,
    trace_all_actions,
)
from utils.common import get_criminals_ids
from utils.informing import send_a_lot_of_messages_safely
from utils.pretty_text import make_pretty
from utils.state import lock_state
from utils.tg import delete_message


class ForgerSaver(RouterHelper):
    async def forger_fakes(
        self, callback_data: UserActionIndexCbData
    ):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data, user_id = await get_game_data_and_user_id(
                game_state=game_state, callback_data=callback_data
            )
            url = game_data["players"][str(user_id)]["url"]
            game_data["forged_roles"] = [user_id]
            await game_state.set_data(game_data)
        markup = choose_fake_role_kb(game_data)
        await self.callback.message.edit_text(
            text=f"Выбери для {url} новую роль", reply_markup=markup
        )

    async def forger_cancels_selection(self):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data = await game_state.get_data()
            game_data["forged_roles"].clear()
            await game_state.set_data(game_data)
        markup = Forger().generate_markup(
            player_id=self.callback.from_user.id, game_data=game_data
        )
        await self.callback.message.edit_text(
            text=Forger.mail_message,
            reply_markup=markup,
        )

    async def forger_selects_documents(self):
        await delete_message(self.callback.message)
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        role_id = cast(RolesLiteral, self.callback.data)
        current_role = get_data_with_roles(role_id)
        forger_roles_key = "forged_roles"
        async with lock_state(game_state):
            game_data: GameCache = await game_state.get_data()
            game_data[forger_roles_key].append(role_id)
            user_id = cast(int, game_data[forger_roles_key][0])
            trace_all_actions(
                callback=self.callback,
                game_data=game_data,
                user_id=user_id,
            )
            await game_state.set_data(game_data)
        user_url = game_data["players"][str(user_id)]["url"]
        forger_url = game_data["players"][
            str(self.callback.from_user.id)
        ]["url"]
        pretty_user_role = make_pretty(current_role.role)
        forger = Forger()
        await send_a_lot_of_messages_safely(
            bot=self.callback.bot,
            users=get_criminals_ids(game_data),
            text=NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + f"{make_pretty(forger.role)} {forger_url} подменил документы "
            f"{user_url} на {pretty_user_role}",
        )
        await send_messages_to_user_and_group(
            callback=self.callback,
            game_data=game_data,
            message_to_user=False,
            current_role=forger,
        )
