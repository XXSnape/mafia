from sqlalchemy import select

from database.dao.base import BaseDAO
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.models import GroupModel
from database.schemas.common import (
    TgIdSchema,
)
from database.schemas.groups import (
    GroupSettingsSchema,
    GroupIdSchema,
)
from database.schemas.settings import DifferentSettingsSchema


class GroupsDao(BaseDAO[GroupModel]):
    model = GroupModel

    async def get_group_settings(
        self,
        group_tg_id: TgIdSchema,
    ) -> GroupSettingsSchema:

        group = await self.find_one_or_none(group_tg_id)
        group_id_schema = GroupIdSchema(group_id=group.id)
        banned_roles = await ProhibitedRolesDAO(
            session=self._session
        ).get_roles_ids_of_banned_roles(group_id_schema)
        order_of_roles = await OrderOfRolesDAO(
            session=self._session
        ).get_roles_ids_of_order_of_roles(group_id_schema)
        settings = DifferentSettingsSchema.model_validate(
            group, from_attributes=True
        )
        return GroupSettingsSchema(
            id=group_id_schema.group_id,
            banned_roles=banned_roles,
            order_of_roles=order_of_roles,
            **settings.model_dump(),
        )

    async def get_every_3_attr(
        self, group_id_schema: GroupIdSchema
    ) -> bool:
        query = select(self.model.mafia_every_3).filter(
            self.model.id == group_id_schema.group_id
        )
        return await self._session.scalar(query)
