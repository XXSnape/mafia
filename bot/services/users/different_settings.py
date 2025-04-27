from cache.cache_types import DifferentSettingsCache
from database.dao.order import OrderOfRolesDAO
from database.dao.settings import SettingsDao
from database.schemas.common import UserTgIdSchema
from database.schemas.settings import (
    FogOfWarSchema,
    DifferentSettingsSchema,
)
from general.collection_of_roles import BASES_ROLES
from keyboards.inline.keypads.fog_of_war import (
    fog_of_war_options_kb,
    different_options_kb,
)
from services.base import RouterHelper
from states.settings import SettingsFsm
from utils.pretty_text import make_build


class DifferentSettings(RouterHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = "different_settings"
        self.message_to_change = (
            "Чтобы изменить настройку, просто нажми на неё\n\n"
            "✅ - настройка включена\n"
            "🚫 - настройка отключена\n\n"
        )

    @staticmethod
    def is_anonymous_mode_enabled(
        fog_of_war_data: DifferentSettingsCache,
    ):
        return (
            fog_of_war_data["show_dead_roles_after_night"]
            and fog_of_war_data["show_dead_roles_after_hanging"]
            and fog_of_war_data["show_roles_died_due_to_inactivity"]
        ) is False

    def _get_info_about_anonymous_mode(
        self, fog_of_war_data: DifferentSettingsCache
    ):
        if self.is_anonymous_mode_enabled(fog_of_war_data):
            mode = "🔴Во время игры некоторые роли будут скрыты"
        else:
            mode = "🟢Во время игры будут показаны актуальные роли"
        return make_build(self.message_to_change + mode)

    async def _start_showing_options(self):
        await self.clear_settings_data()
        settings_dao = SettingsDao(session=self.session)
        user_setting = await settings_dao.find_one_or_none(
            UserTgIdSchema(user_tg_id=self.callback.from_user.id)
        )
        different_settings_schema = (
            DifferentSettingsSchema.model_validate(
                user_setting, from_attributes=True
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
        settings_dao = SettingsDao(session=self.session)
        await settings_dao.update(
            filters=UserTgIdSchema(
                user_tg_id=self.callback.from_user.id
            ),
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
        user_schema = UserTgIdSchema(
            user_tg_id=self.callback.from_user.id
        )
        order_of_roles_dao = OrderOfRolesDAO(session=self.session)
        roles = (
            await order_of_roles_dao.get_roles_ids_of_order_of_roles(
                user_schema
            )
        )
        if roles != list(BASES_ROLES):
            await order_of_roles_dao.delete(user_schema)
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
