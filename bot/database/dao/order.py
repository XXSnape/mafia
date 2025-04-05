from collections.abc import Iterable

from sqlalchemy import select

from cache.cache_types import RolesLiteral
from database.dao.base import BaseDAO
from database.models import OrderModel, RoleModel
from database.schemas.common import UserTgId


class OrderOfRolesDAO(BaseDAO[OrderModel]):
    model = OrderModel

    async def get_roles_ids_of_order_of_roles(
        self,
        user_filter: UserTgId,
    ) -> Iterable[RolesLiteral]:
        query = (
            select(RoleModel.key)
            .select_from(self.model)
            .join(RoleModel)
            .filter(self.model.user_tg_id == user_filter.user_tg_id)
            .order_by(self.model.number)
        )
        return (await self._session.scalars(query)).all()
