from datetime import datetime

from sqlalchemy import select, func, Integer

from database.dao.base import BaseDAO
from database.dao.groups import GroupsDao
from database.models import GameModel, ResultModel
from database.schemas.common import TgId, IdSchema
from database.schemas.games import BeginningOfGameSchema
from database.schemas.groups import GroupIdSchema


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

    async def get_winning_groupings(
        self, group_id_filter: GroupIdSchema
    ):
        query = (
            select(
                func.count(self.model.winning_group),
                self.model.winning_group,
            )
            .group_by(self.model.winning_group)
            .filter_by(**group_id_filter.model_dump())
            .filter(
                self.model.end.is_not(None),
                self.model.winning_group.is_not(None),
            )
        )
        result = await self._session.execute(query)
        return result.all()

    async def get_results(self, group_id_filter: GroupIdSchema):
        query = (
            select(
                func.count(self.model.id).label("number_of_games"),
                func.cast(
                    func.avg(self.model.number_of_nights), Integer
                ).label("nights_lived_count"),
                func.avg(self.model.end - self.model.start).label(
                    "average_time"
                ),
                func.count(ResultModel.user_tg_id),
            )
            .filter_by(**group_id_filter.model_dump())
            .filter(
                self.model.end.is_not(None),
                self.model.winning_group.is_not(None),
            )
            .group_by(self.model.group_id)
            .join(ResultModel, ResultModel.game_id == self.model.id)
        )
        print(query)
        result = await self._session.execute(query)
        return result.one_or_none()

    async def get_average_number_of_players(
        self, group_id_filter: GroupIdSchema
    ):
        # game group count

        sub_query = (
            select(
                func.count(ResultModel.user_tg_id).label(
                    "number_of_players"
                )
            )
            .select_from(self.model)
            .join(ResultModel, ResultModel.game_id == self.model.id)
            .group_by(self.model.id, self.model.group_id)
            .filter(
                self.model.group_id == group_id_filter.group_id,
                self.model.end.is_not(None),
                self.model.winning_group.is_not(None),
            )
        ).subquery()
        print(sub_query)
        #
        query = select(
            func.avg(sub_query.c.number_of_players)
        ).select_from(sub_query)
        print(query)
        return await self._session.scalar(query)
