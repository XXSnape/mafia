from sqlalchemy import select

from database.dao.base import BaseDAO
from database.models import OrderModel, RoleModel
from database.schemas.roles import UserTgId


class OrderOfRolesDAO(BaseDAO[OrderModel]):
    model = OrderModel

    async def get_key_of_order_of_roles(
        self,
        user_filter: UserTgId,
    ):
        query = (
            select(RoleModel.key)
            .select_from(self.model)
            .join(RoleModel)
            .filter(self.model.user_tg_id == user_filter.user_tg_id)
            .order_by(self.model.number)
        )
        return (await self._session.scalars(query)).all()
