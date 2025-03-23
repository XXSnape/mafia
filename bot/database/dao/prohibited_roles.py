from sqlalchemy import select

from database.dao.base import BaseDAO
from database.models import ProhibitedRoleModel, RoleModel
from database.schemas.roles import UserTgId


class ProhibitedRolesDAO(BaseDAO[ProhibitedRoleModel]):
    model = ProhibitedRoleModel

    async def get_banned_roles_names(self, user_filter: UserTgId):
        result = await self.find_all(user_filter)
        return [record.role for record in result]

    async def get_keys_of_banned_roles(
        self,
        user_filter: UserTgId,
    ):
        query = (
            select(RoleModel.key)
            .select_from(self.model)
            .join(RoleModel)
            .filter(self.model.user_tg_id == user_filter.user_tg_id)
        )
        return (await self._session.scalars(query)).all()
