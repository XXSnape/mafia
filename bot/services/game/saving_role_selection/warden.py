from aiogram.fsm.context import FSMContext

from cache.cache_types import GameCache
from constants.output import NUMBER_OF_NIGHT
from keyboards.inline.keypads.mailing import selection_to_warden_kb
from services.base import RouterHelper
from services.game.actions_at_night import (
    get_game_state_and_data,
    trace_all_actions,
    send_messages_to_group_and_user,
)
from mafia.roles import Warden
from utils.pretty_text import make_build
from utils.tg import delete_message


class WardenSaver(RouterHelper):

    async def _generate_markup_after_selection(
        self, game_data: GameCache, game_state: FSMContext
    ):
        markup = selection_to_warden_kb(
            game_data=game_data, user_id=self.callback.from_user.id
        )
        await self.callback.message.edit_reply_markup(
            reply_markup=markup
        )
        await game_state.set_data(game_data)

    async def supervisor_collects_information(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        checked = game_data["checked_for_the_same_groups"]
        processed_user_id = int(self.callback.data)
        if len(checked) == 1 and checked[0] == processed_user_id:
            checked.clear()
            await self._generate_markup_after_selection(
                game_state=game_state,
                game_data=game_data,
            )
            return
        elif len(checked) == 0:
            checked.append(processed_user_id)
            await self._generate_markup_after_selection(
                game_state=game_state,
                game_data=game_data,
            )
            return

        checked.append(processed_user_id)
        user1_id: int = checked[0]
        user2_id: int = checked[1]
        for user_id in [user1_id, user2_id]:
            await trace_all_actions(
                callback=self.callback,
                game_data=game_data,
                user_id=user_id,
                message_to_group=False,
                message_to_user=False,
                current_role=Warden(),
            )
        user1_url = game_data["players"][str(user1_id)]["url"]
        user2_url = game_data["players"][str(user2_id)]["url"]
        await send_messages_to_group_and_user(
            callback=self.callback,
            game_data=game_data,
            message_to_user=f"Ты решил проверить на принадлежность одной группировки {user1_url} и {user2_url}",
            current_role=Warden(),
        )
        await game_state.set_data(game_data)
