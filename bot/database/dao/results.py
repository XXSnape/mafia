from sqlalchemy import select, func, Integer, desc

from database.dao.base import BaseDAO
from database.models import ResultModel
from database.schemas.common import UserTgId


class ResultsDao(BaseDAO[ResultModel]):
    model = ResultModel

    async def get_results(self, user_tg_id: UserTgId):
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
            )
            .filter_by(**user_tg_id.model_dump())
            .group_by(self.model.role_id)
            .order_by(desc("money_sum"))
        )
        print("q", query)
        result = await self._session.execute(query)
        return result.all()
