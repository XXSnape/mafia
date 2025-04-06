from datetime import datetime

from database.dao.base import BaseDAO
from database.dao.groups import GroupsDao
from database.models import GameModel
from database.schemas.common import TgId
from database.schemas.games import BeginningOfGameSchema


class GamesDao(BaseDAO[GameModel]):
    model = GameModel

    async def create_game(self, tg_id: TgId, start: datetime) -> int:
        group = await GroupsDao(
            session=self._session
        ).find_one_or_none(filters=tg_id)
        game = await self.add(
            BeginningOfGameSchema(group_id=group.id, start=start)
        )
        return game.id
