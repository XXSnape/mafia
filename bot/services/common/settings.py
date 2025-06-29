from collections.abc import Awaitable, Callable
from typing import Concatenate

from aiogram.exceptions import TelegramAPIError
from cache.cache_types import (
    AllSettingsCache,
    DifferentSettingsCache,
    PersonalSettingsCache,
)
from database.dao.groups import GroupsDao
from database.schemas.common import (
    TgIdSchema,
)
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from keyboards.inline.keypads.different_settings import (
    check_for_settings,
    get_different_settings_buttons,
    get_for_of_war_buttons,
)
from keyboards.inline.keypads.settings import (
    select_setting_kb,
    set_up_group_kb,
)
from services.base import RouterHelper
from services.users.banned_roles import RoleAttendant
from services.users.order_of_roles import RoleManager
from utils.pretty_text import (
    get_minutes_and_seconds_text,
    make_build,
)
from utils.tg import check_user_for_admin_rights, delete_message


def cant_write_to_user[R, **P](
    async_func: Callable[
        Concatenate["SettingsRouter", P],
        Awaitable[R | None],
    ],
):
    async def wrapper(
        self: "SettingsRouter", *args: P.args, **kwargs: P.kwargs
    ) -> R | None:
        try:
            return await async_func(self, *args, **kwargs)
        except TelegramAPIError:
            await self.message.answer(
                make_build(
                    "❗️Для просмотра настроек сначала напишите боту /start в личные сообщения"
                )
            )

    return wrapper


class SettingsRouter(RouterHelper):
    async def _suggest_changing_settings(self):
        await self.callback.message.edit_text(
            text=make_build(
                "⚙️Выбери, что конкретно хочешь настроить"
            ),
            reply_markup=select_setting_kb(),
        )

    @staticmethod
    def get_other_settings_text(
        settings: DifferentSettingsCache,
    ) -> str:
        buttons = (
            get_for_of_war_buttons()
            + get_different_settings_buttons()
        )
        check_for_settings(
            buttons=buttons, different_settings=settings
        )
        different_settings_text = "\n\n".join(
            btn.text for btn in buttons
        )
        return make_build(
            different_settings_text
            + (
                f"\n\n{get_minutes_and_seconds_text(message='Продолжительность ночи - ', 
                                            seconds=settings['time_for_night'])}\n\n"
                f"{get_minutes_and_seconds_text(message='Продолжительность дня - ', 
                                            seconds=settings['time_for_day'])}\n\n"
                f"{get_minutes_and_seconds_text(message='Продолжительность голосования - ', 
                                            seconds=settings['time_for_voting'])}\n\n"
                f"{get_minutes_and_seconds_text(message='Продолжительность процесса подтверждения о повешении - ', 
                                            seconds=settings['time_for_confirmation'])}"
            )
        )

    @cant_write_to_user
    async def get_group_settings(self):
        await delete_message(self.message)
        groups_dao = GroupsDao(session=self.session)
        group_tg_id = self.message.chat.id
        await self.get_group_or_create()
        group_settings = await groups_dao.get_group_settings(
            group_tg_id=TgIdSchema(tg_id=group_tg_id)
        )
        is_user_admin = await check_user_for_admin_rights(
            bot=self.message.bot,
            chat_id=group_tg_id,
            user_id=self.message.from_user.id,
        )
        group_name = make_build(
            f"🔧Настройки группы «{self.message.chat.title}»\n\n"
        )

        banned_roles_text = RoleAttendant.get_banned_roles_text(
            roles_ids=group_settings.banned_roles
        )
        order_of_roles_text = RoleManager.get_current_order_text(
            selected_roles=group_settings.order_of_roles,
            to_save=False,
        )
        other_settings_text = self.get_other_settings_text(
            settings=group_settings.model_dump()
        )
        await self.message.bot.send_message(
            chat_id=self.message.from_user.id,
            text=group_name + other_settings_text,
        )
        await self.message.bot.send_message(
            chat_id=self.message.from_user.id,
            text=group_name + order_of_roles_text,
        )
        await self.message.bot.send_message(
            chat_id=self.message.from_user.id,
            text=group_name + banned_roles_text,
        )

        if is_user_admin:
            await self.message.bot.send_message(
                chat_id=self.message.from_user.id,
                text=make_build(
                    f"❗️Ты можешь поменять настройки группы «{self.message.chat.title}»"
                    f" с помощью кнопки ниже:"
                ),
                reply_markup=set_up_group_kb(
                    group_id=group_settings.id,
                ),
            )

    async def back_to_settings(self):
        await self.clear_settings_data()
        await self._suggest_changing_settings()

    async def start_changing_settings(
        self, callback_data: GroupSettingsCbData
    ):
        data: PersonalSettingsCache = await self.state.get_data()
        data["settings"] = AllSettingsCache(
            group_id=callback_data.group_id
        )
        await self.state.set_data(data)
        await self._suggest_changing_settings()
