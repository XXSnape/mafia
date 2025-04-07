from sqlalchemy import select, func, case, Integer

from database.dao.base import BaseDAO
from database.models import RateModel
from database.schemas.common import UserTgId


class RatesDao(BaseDAO[RateModel]):
    model = RateModel

    async def get_results(self, user_tg_id: UserTgId):
        query = select(
            func.count(self.model.id).label("count"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            self.model.is_winner.is_(True),
                            self.model.money,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("money"),
            func.coalesce(
                func.sum(func.cast(self.model.is_winner, Integer)), 0
            ).label("is_winner_count"),
        ).filter_by(**user_tg_id.model_dump())
        print(query)
        result = await self._session.execute(query)
        return result.one_or_none()
