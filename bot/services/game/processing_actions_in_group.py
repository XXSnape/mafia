from cache.cache_types import GameCache
from services.base import RouterHelper
from services.game.roles import Prosecutor
from utils.tg import delete_message


class GroupManager(RouterHelper):
    async def delete_message_from_non_players(self):
        game_data: GameCache = await self.state.get_data()
        if (
            self.message.from_user.id not in game_data["players_ids"]
        ) or self.message.from_user.id == Prosecutor().get_processed_user_id(
            game_data
        ):
            await delete_message(message=self.message)
