from constants.output import NUMBER_OF_NIGHT
from services.base import RouterHelper
from services.game.actions_at_night import get_game_state_and_data
from services.game.roles import Analyst
from utils.tg import delete_message


class AnalystSaver(RouterHelper):
    async def analyst_assumes_draw(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        game_data[Analyst.processed_users_key].append(0)
        await delete_message(self.callback.message)
        await self.callback.message.answer(
            text=NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + "Ты предположил, что никого не повесят днём"
        )
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=Analyst.message_to_group_after_action,
        )
        await game_state.set_data(game_data)
