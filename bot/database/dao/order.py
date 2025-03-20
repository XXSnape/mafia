from database.dao.base import BaseDAO
from database.models import OrderModel
from database.schemas.roles import UserTgId, OrderOfRolesSchema
from general.collection_of_roles import get_data_with_roles


class OrderOfRolesDAO(BaseDAO[OrderModel]):
    model = OrderModel

    async def save_order_of_roles(
        self, user_id: int, roles: list[str]
    ):
        await self.delete(UserTgId(user_tg_id=user_id))
        all_roles = get_data_with_roles()
        order_of_roles = [
            OrderOfRolesSchema(
                user_tg_id=user_id,
                role=all_roles[role].role,
                number=number,
            )
            for number, role in enumerate(roles, 1)
        ]
        await self.add_many(order_of_roles)
