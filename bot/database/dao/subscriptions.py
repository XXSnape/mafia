from database.dao.base import BaseDAO
from database.models import SubscriptionModel
from loguru import logger
from sqlalchemy import delete


class SubscriptionsDAO(BaseDAO[SubscriptionModel]):
    model = SubscriptionModel

    async def delete_subscriptions(self, ids: set[int]):
        if not ids:
            return
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = await self._session.execute(stmt)
        await self._session.flush()
        logger.info(
            "В таблице {} удалено {} записей.",
            self.model.__name__,
            result.rowcount,
        )
