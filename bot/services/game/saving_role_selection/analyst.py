from mafia.roles import Analyst
from services.base import RouterHelper
from services.game.game_assistants import (
    send_messages_to_user_and_group,
    get_game_state_by_user_state,
    remove_from_expected,
)
from utils.state import lock_state
from utils.tg import delete_message


class AnalystSaver(RouterHelper):
    async def analyst_assumes_draw(self):
        await delete_message(self.callback.message)
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data = await game_state.get_data()
            game_data[Analyst.processed_users_key] = [0]
            remove_from_expected(
                callback=self.callback, game_data=game_data
            )
            await game_state.set_data(game_data)
        await send_messages_to_user_and_group(
            callback=self.callback,
            game_data=game_data,
            message_to_user="Ты предположил, что никого не повесят днём",
            current_role=Analyst(),
        )
