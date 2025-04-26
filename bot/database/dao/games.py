from datetime import datetime, timedelta

from database.dao.base import BaseDAO
from database.dao.groups import GroupsDao
from database.models import GameModel, ResultModel
from database.schemas.common import TgIdSchema
from database.schemas.games import BeginningOfGameSchema
from database.schemas.groups import GroupIdSchema
from sqlalchemy import Integer, desc, func, select


class GamesDao(BaseDAO[GameModel]):
    model = GameModel

    async def create_game(
        self, tg_id: TgIdSchema, start: datetime
    ) -> int:
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
                func.count(self.model.winning_group).label(
                    "number_of_wins"
                ),
                self.model.winning_group,
            )
            .group_by(self.model.winning_group)
            .filter_by(**group_id_filter.model_dump())
            .filter(
                self.model.end.is_not(None),
                self.model.winning_group.is_not(None),
            )
            .order_by(desc("number_of_wins"))
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
            )
            .filter_by(**group_id_filter.model_dump())
            .filter(
                self.model.end.is_not(None),
                self.model.winning_group.is_not(None),
            )
            .group_by(self.model.group_id)
        )
        result = await self._session.execute(query)
        return result.one_or_none()

    async def get_average_number_of_players(
        self, group_id_filter: GroupIdSchema
    ):

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
        query = select(
            func.cast(
                func.avg(sub_query.c.number_of_players), Integer
            )
        ).select_from(sub_query)
        return await self._session.scalar(query)

    async def get_statistics_of_players_by_group(
        self, group_id_filter: GroupIdSchema
    ):
        query = (
            select(
                ResultModel.user_tg_id,
                func.count(ResultModel.user_tg_id).label(
                    "number_of_games"
                ),
                func.sum(
                    func.cast(ResultModel.is_winner, Integer)
                ).label("number_of_wins"),
                func.cast(
                    func.sum(
                        func.cast(ResultModel.is_winner, Integer)
                    )
                    / func.count(ResultModel.user_tg_id)
                    * 100,
                    Integer,
                ).label("efficiency"),
            )
            .select_from(self.model)
            .join(ResultModel, ResultModel.game_id == self.model.id)
            .filter(
                self.model.group_id == group_id_filter.group_id,
                self.model.end.is_not(None),
                self.model.winning_group.is_not(None),
                datetime.now() - self.model.end < timedelta(days=30),
            )
            .group_by(ResultModel.user_tg_id)
            .having(
                func.count(ResultModel.user_tg_id) >= 3,
            )
            .order_by(desc("number_of_games"), desc("efficiency"))
            .limit(15)
        )
        result = await self._session.execute(query)
        return result.all()
