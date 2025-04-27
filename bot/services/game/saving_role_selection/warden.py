from aiogram.fsm.context import FSMContext
from cache.cache_types import GameCache
from keyboards.inline.keypads.mailing import selection_to_warden_kb
from mafia.roles import Warden
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_state_by_user_state,
    remove_from_expected,
    send_messages_to_user_and_group,
    trace_all_actions,
)
from utils.state import lock_state
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
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        processed_user_id = int(self.callback.data)
        async with lock_state(game_state):
            game_data = await game_state.get_data()
            checked = game_data["checked_for_the_same_groups"]
            if len(checked) == 0:
                checked[:] = [processed_user_id]
                await self._generate_markup_after_selection(
                    game_state=game_state,
                    game_data=game_data,
                )
                return
            elif (
                len(checked) == 1 and checked[0] == processed_user_id
            ):
                checked.clear()
                await self._generate_markup_after_selection(
                    game_state=game_state,
                    game_data=game_data,
                )
                return
            await delete_message(self.callback.message)
            checked.append(processed_user_id)
            user1_id: int = checked[0]
            user2_id: int = checked[1]
            for user_id in [user1_id, user2_id]:
                trace_all_actions(
                    callback=self.callback,
                    game_data=game_data,
                    user_id=user_id,
                    need_to_remove_from_expected=False,
                )
            remove_from_expected(
                callback=self.callback, game_data=game_data
            )
            await game_state.set_data(game_data)

        user1_url = game_data["players"][str(user1_id)]["url"]
        user2_url = game_data["players"][str(user2_id)]["url"]
        await send_messages_to_user_and_group(
            callback=self.callback,
            game_data=game_data,
            message_to_user=f"Ты решил проверить на принадлежность "
            f"одной группировки {user1_url} и {user2_url}",
            current_role=Warden(),
            message_to_group=game_data["settings"][
                "is_fog_of_war_on"
            ]
            is False,
        )
