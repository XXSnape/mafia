from database.dao.base import BaseDAO
from database.models import ProhibitedRoleModel, RoleModel
from database.schemas.common import UserTgIdSchema
from sqlalchemy import select


class ProhibitedRolesDAO(BaseDAO[ProhibitedRoleModel]):
    model = ProhibitedRoleModel

    async def get_roles_ids_of_banned_roles(
        self,
        user_filter: UserTgIdSchema,
    ):
        query = (
            select(RoleModel.key)
            .select_from(self.model)
            .join(RoleModel)
            .filter(self.model.user_tg_id == user_filter.user_tg_id)
        )
        return (await self._session.scalars(query)).all()
