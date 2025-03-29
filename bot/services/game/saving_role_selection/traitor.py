import asyncio

from constants.output import NUMBER_OF_NIGHT
from keyboards.inline.callback_factory.recognize_user import UserActionIndexCbData
from services.base import RouterHelper
from services.game.actions_at_night import take_action_and_save_data
from services.game.roles import Traitor, Mafia
from utils.utils import make_pretty


class TraitorSaver(RouterHelper):
    async def traitor_finds_out(self, callback_data: UserActionIndexCbData):
        game_state, game_data, user_id = (
            await take_action_and_save_data(
                callback=self.callback,
                callback_data=callback_data,
                state=self.state,
                dispatcher=self.dispatcher,
            )
        )
        url = game_data["players"][str(user_id)]["url"]
        role = game_data["players"][str(user_id)]["pretty_role"]
        await asyncio.gather(
            *(
                self.callback.bot.send_message(
                    chat_id=player_id,
                    text=NUMBER_OF_NIGHT.format(
                        game_data["number_of_night"]
                    )
                         + f"{make_pretty(Traitor.role)} проверил и узнал, что {url} - {role}",
                )
                for player_id in game_data[Mafia.roles_key]
                                 + game_data[Traitor.roles_key]
            )
        )
