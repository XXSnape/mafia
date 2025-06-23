from database.dao.base import BaseDAO
from database.models import ProhibitedRoleModel, RoleModel
from database.schemas.groups import GroupIdSchema
from sqlalchemy import select


class ProhibitedRolesDAO(BaseDAO[ProhibitedRoleModel]):
    model = ProhibitedRoleModel

    async def get_roles_ids_of_banned_roles(
        self,
        group_filter: GroupIdSchema,
    ):
        query = (
            select(RoleModel.key)
            .select_from(self.model)
            .join(RoleModel)
            .filter(self.model.group_id == group_filter.group_id)
        )
        return (await self._session.scalars(query)).all()
