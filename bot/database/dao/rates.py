from sqlalchemy import select, func, case, Integer

from database.dao.base import BaseDAO
from database.models import RateModel
from database.schemas.common import UserTgId


class RatesDao(BaseDAO[RateModel]):
    model = RateModel

    async def get_results(self, user_tg_id: UserTgId):
        query = select(
            func.count().label("count"),
            func.sum(
                case(
                    (
                        self.model.is_winner.is_(True),
                        self.model.money,
                    ),
                    else_=0,
                )
            ).label("money"),
            func.sum(func.cast(self.model.is_winner, Integer)).label(
                "is_winner_count"
            ),
        ).filter_by(**user_tg_id.model_dump())
        result = await self._session.scalar(query)
        return result
