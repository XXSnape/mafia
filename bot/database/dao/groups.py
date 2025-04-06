from database.dao.base import BaseDAO
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.dao.settings import SettingsDao
from database.models import GroupModel
from database.schemas.common import TgId, IdSchema, UserTgId
from database.schemas.groups import GroupSettingsSchema


class GroupsDao(BaseDAO[GroupModel]):
    model = GroupModel

    async def get_group_settings(
        self, group_tg_id: TgId
    ) -> GroupSettingsSchema:
        group = await self.find_one_or_none(group_tg_id)
        if group.setting_id is None:
            return GroupSettingsSchema(id=group.id)
        settings_of_group = await SettingsDao(
            session=self._session
        ).find_one_or_none(IdSchema(id=group.setting_id))
        user_filter = UserTgId(
            user_tg_id=settings_of_group.user_tg_id
        )
        banned_roles = await ProhibitedRolesDAO(
            session=self._session
        ).get_roles_ids_of_banned_roles(user_filter)
        order_of_roles = await OrderOfRolesDAO(
            session=self._session
        ).get_roles_ids_of_order_of_roles(user_filter)
        return GroupSettingsSchema(
            id=group.id,
            banned_roles=banned_roles,
            order_of_roles=order_of_roles,
            time_for_night=settings_of_group.time_for_night,
            time_for_day=settings_of_group.time_for_day,
        )
