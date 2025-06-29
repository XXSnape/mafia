from cache.cache_types import DifferentSettingsCache
from database.dao.groups import GroupsDao
from database.dao.order import OrderOfRolesDAO
from database.schemas.settings import (
    DifferentSettingsSchema,
)
from general.collection_of_roles import BASES_ROLES
from keyboards.inline.keypads.different_settings import (
    different_options_kb,
    fog_of_war_options_kb,
)
from services.base import RouterHelper
from utils.pretty_text import make_build


class DifferentSettings(RouterHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = "different_settings"
        self.message_to_change = (
            "⚙️Чтобы изменить настройку, просто нажми на неё\n\n"
            "✅ - настройка включена\n"
            "❌ - настройка отключена\n\n"
        )

    def _get_info_about_anonymous_mode(
        self, fog_of_war_data: DifferentSettingsCache
    ):
        if not fog_of_war_data["show_roles_after_death"]:
            mode = (
                "🔴Во время игры роли будут скрыты и "
                "не будет сообщений о ночных действиях"
            )
        else:
            mode = "🟢Во время игры будут показаны актуальные роли и сообщения в группе после действий ночью"
        return make_build(self.message_to_change + mode)

    async def _start_showing_options(self):
        group_schema = await self.get_group_id_schema(id_schema=True)

        await self.clear_settings_data()
        group = await GroupsDao(
            session=self.session
        ).find_one_or_none(group_schema)
        different_settings_schema = (
            DifferentSettingsSchema.model_validate(
                group, from_attributes=True
            )
        )
        different_settings_data: DifferentSettingsCache = (
            different_settings_schema.model_dump()
        )
        await self.set_settings_data(different_settings_data)
        return different_settings_data

    async def show_fog_of_war_options(self):
        fog_of_war_data = await self._start_showing_options()
        await self.callback.message.edit_text(
            self._get_info_about_anonymous_mode(fog_of_war_data),
            reply_markup=fog_of_war_options_kb(
                fog_of_war=fog_of_war_data
            ),
        )

    async def update_settings(self):
        different_settings_data: DifferentSettingsCache = (
            await self.get_settings_data()
        )
        different_settings_data[self.callback.data] = not (
            different_settings_data[self.callback.data]
        )
        groups_dao = GroupsDao(session=self.session)
        group_schema = await self.get_group_id_schema(id_schema=True)
        await groups_dao.update(
            filters=group_schema,
            values=DifferentSettingsSchema.model_validate(
                different_settings_data
            ),
        )
        await self.set_settings_data(different_settings_data)
        return different_settings_data

    async def change_settings_for_non_deceased_roles(self):
        fog_of_war_data: DifferentSettingsCache = (
            await self.update_settings()
        )
        await self.callback.message.edit_reply_markup(
            reply_markup=fog_of_war_options_kb(
                fog_of_war=fog_of_war_data
            )
        )

    async def change_settings_related_to_deceased_roles(self):
        fog_of_war_data: DifferentSettingsCache = (
            await self.update_settings()
        )
        await self.callback.message.edit_text(
            self._get_info_about_anonymous_mode(fog_of_war_data),
            reply_markup=fog_of_war_options_kb(
                fog_of_war=fog_of_war_data
            ),
        )

    async def show_common_settings_options(self):
        different_data = await self._start_showing_options()
        await self.callback.message.edit_text(
            text=make_build(self.message_to_change),
            reply_markup=different_options_kb(
                different_settings=different_data
            ),
        )

    async def change_different_settings(self):
        different_data: DifferentSettingsCache = (
            await self.update_settings()
        )
        await self.callback.message.edit_reply_markup(
            reply_markup=different_options_kb(
                different_settings=different_data
            )
        )

    async def handle_mafia_every_3(self):
        different_data: DifferentSettingsCache = (
            await self.update_settings()
        )
        group_schema = await self.get_group_id_schema()
        order_of_roles_dao = OrderOfRolesDAO(session=self.session)
        roles = (
            await order_of_roles_dao.get_roles_ids_of_order_of_roles(
                group_schema
            )
        )
        if roles != list(BASES_ROLES):
            await order_of_roles_dao.delete(group_schema)
            await self.callback.answer(
                "❗️❗️❗️ВНИМАНИЕ! ПОРЯДОК РОЛЕЙ СБРОШЕН!\n\n"
                "Настрой его заново",
                show_alert=True,
            )
        await self.callback.message.edit_reply_markup(
            reply_markup=different_options_kb(
                different_settings=different_data
            )
        )
