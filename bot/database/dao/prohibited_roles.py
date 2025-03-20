from database.dao.base import BaseDAO
from database.models import ProhibitedRoleModel
from database.schemas.roles import ProhibitedRoleSchema, UserTgId


class ProhibitedRolesDAO(BaseDAO[ProhibitedRoleModel]):
    model = ProhibitedRoleModel

    async def save_new_prohibited_roles(
        self, user_id: int, roles: list[str]
    ):
        await self.delete(UserTgId(user_tg_id=user_id))
        prohibited_roles = [
            ProhibitedRoleSchema(user_tg_id=user_id, role=role)
            for role in roles
        ]
        await self.add_many(prohibited_roles)

    async def get_banned_roles(self, user_id: int):
        result = await self.find_all(UserTgId(user_tg_id=user_id))
        return [record.role for record in result]
