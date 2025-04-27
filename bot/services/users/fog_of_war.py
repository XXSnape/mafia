from cache.cache_types import DifferentSettingsCache
from database.dao.settings import SettingsDao
from database.schemas.common import UserTgIdSchema
from database.schemas.settings import FogOfWarSchema
from keyboards.inline.keypads.fog_of_war import fog_of_war_options_kb
from services.base import RouterHelper
from states.settings import SettingsFsm
from utils.pretty_text import make_build


class FogOfWar(RouterHelper):

    @staticmethod
    def is_anonymous_mode_enabled(
        fog_of_war_data: DifferentSettingsCache,
    ):
        return (
            fog_of_war_data["show_dead_roles_after_night"]
            and fog_of_war_data["show_dead_roles_after_hanging"]
            and fog_of_war_data["show_roles_died_due_to_inactivity"]
        ) is False

    def get_message(self, fog_of_war_data: DifferentSettingsCache):
        message = (
            "Чтобы изменить настройку, просто нажми на неё\n\n"
            "✅ - настройка включена\n"
            "🚫 - настройка отключена\n\n"
        )
        if self.is_anonymous_mode_enabled(fog_of_war_data):
            mode = "🔴Во время игры некоторые роли будут скрыты"
        else:
            mode = "🟢Во время игры будут показаны актуальные роли"
        return make_build(message + mode)

    async def show_options(self):
        await self.state.clear()
        await self.state.set_state(SettingsFsm.FOG_OF_WAR)
        settings_dao = SettingsDao(session=self.session)
        user_setting = await settings_dao.find_one_or_none(
            UserTgIdSchema(user_tg_id=self.callback.from_user.id)
        )
        fog_of_war_schema = FogOfWarSchema.model_validate(
            user_setting, from_attributes=True
        )
        fog_of_war_data: DifferentSettingsCache = (
            fog_of_war_schema.model_dump()
        )
        await self.state.set_data(fog_of_war_data)
        await self.callback.message.edit_text(
            self.get_message(fog_of_war_data),
            reply_markup=fog_of_war_options_kb(
                fog_of_war=fog_of_war_data
            ),
        )

    async def update_settings(self):
        fog_of_war_data: DifferentSettingsCache = (
            await self.state.get_data()
        )
        fog_of_war_data[self.callback.data] = not (
            fog_of_war_data[self.callback.data]
        )
        settings_dao = SettingsDao(session=self.session)
        await settings_dao.update(
            filters=UserTgIdSchema(
                user_tg_id=self.callback.from_user.id
            ),
            values=FogOfWarSchema.model_validate(fog_of_war_data),
        )
        await self.state.set_data(fog_of_war_data)
        return fog_of_war_data

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
            self.get_message(fog_of_war_data),
            reply_markup=fog_of_war_options_kb(
                fog_of_war=fog_of_war_data
            ),
        )
