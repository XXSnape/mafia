from database.dao.base import BaseDAO
from database.models import ResultModel
from database.schemas.common import UserTgIdSchema
from sqlalchemy import Integer, desc, func, select


class ResultsDao(BaseDAO[ResultModel]):
    model = ResultModel

    async def get_results(self, user_tg_id: UserTgIdSchema):
        query = (
            select(
                self.model.role_id,
                func.count().label("number_of_games"),
                func.sum(
                    func.cast(self.model.is_winner, Integer)
                ).label("is_winner_count"),
                func.sum(self.model.nights_lived).label(
                    "nights_lived_count"
                ),
                func.sum(self.model.money).label("money_sum"),
                func.cast(
                    func.sum(
                        func.cast(self.model.is_winner, Integer)
                    )
                    / func.count()
                    * 100,
                    Integer,
                ).label("efficiency"),
            )
            .filter_by(**user_tg_id.model_dump())
            .group_by(self.model.role_id)
            .order_by(desc("money_sum"))
        )
        result = await self._session.execute(query)
        return result.all()
