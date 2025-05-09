from database.dao.base import BaseDAO
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.dao.settings import SettingsDao
from database.models import GroupModel
from database.schemas.common import (
    IdSchema,
    TgIdSchema,
    UserTgIdSchema,
)
from database.schemas.groups import GroupSettingsSchema
from database.schemas.settings import DifferentSettingsSchema
from general.collection_of_roles import BASES_ROLES


class GroupsDao(BaseDAO[GroupModel]):
    model = GroupModel

    async def get_group_settings(
        self,
        group_tg_id: TgIdSchema,
        user_tg_id: UserTgIdSchema | None = None,
    ) -> GroupSettingsSchema:

        group = await self.find_one_or_none(group_tg_id)
        if group.setting_id is None and user_tg_id is None:
            return GroupSettingsSchema(
                id=group.id,
                banned_roles=[],
                order_of_roles=list(BASES_ROLES),
                is_there_settings=False,
                **DifferentSettingsSchema().model_dump(),
            )
        elif group.setting_id is not None:
            settings_of_group = await SettingsDao(
                session=self._session
            ).find_one_or_none(IdSchema(id=group.setting_id))
            user_tg_id = UserTgIdSchema(
                user_tg_id=settings_of_group.user_tg_id
            )
        else:
            settings_of_group = await SettingsDao(
                session=self._session
            ).find_one_or_none(user_tg_id)

        banned_roles = await ProhibitedRolesDAO(
            session=self._session
        ).get_roles_ids_of_banned_roles(user_tg_id)
        order_of_roles = await OrderOfRolesDAO(
            session=self._session
        ).get_roles_ids_of_order_of_roles(user_tg_id)
        model = (
            DifferentSettingsSchema.model_validate(
                settings_of_group, from_attributes=True
            )
            if settings_of_group
            else DifferentSettingsSchema()
        )
        return GroupSettingsSchema(
            id=group.id,
            banned_roles=banned_roles,
            order_of_roles=order_of_roles,
            is_there_settings=True,
            **model.model_dump(),
        )
