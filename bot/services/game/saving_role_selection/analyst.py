from services.base import RouterHelper
from services.game.actions_at_night import (
    get_game_state_and_data,
    send_messages_and_remove_from_expected,
)
from mafia.roles import Analyst


class AnalystSaver(RouterHelper):
    async def analyst_assumes_draw(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        game_data[Analyst.processed_users_key].append(0)
        await send_messages_and_remove_from_expected(
            callback=self.callback,
            game_data=game_data,
            message_to_user="Ты предположил, что никого не повесят днём",
            current_role=Analyst(),
        )
        await game_state.set_data(game_data)
