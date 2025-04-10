from collections.abc import Callable, Awaitable
from typing import Concatenate

from aiogram.exceptions import TelegramAPIError

from database.dao.settings import SettingsDao
from database.schemas.groups import GroupSettingIdSchema
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from services.base import RouterHelper

from database.dao.groups import GroupsDao
from database.schemas.common import (
    TgIdSchema,
    IdSchema,
    UserTgIdSchema,
)
from keyboards.inline.keypads.settings import set_up_group_kb
from middlewares.db import (
    DatabaseMiddlewareWithoutCommit,
)
from services.users.banned_roles import RoleAttendant
from services.users.order_of_roles import RoleManager
from utils.pretty_text import make_build
from utils.tg import check_user_for_admin_rights, delete_message


def checking_for_ability_to_change_settings[R, **P](
    async_func: Callable[
        Concatenate["SettingsRouter", GroupSettingsCbData, P],
        Awaitable[R | None],
    ],
):
    async def wrapper(
        self: "SettingsRouter",
        callback_data: GroupSettingsCbData,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R | None:
        groups_dao = GroupsDao(session=self.session)
        group = await groups_dao.find_one_or_none(
            IdSchema(id=callback_data.group_id)
        )
        is_user_admin = await check_user_for_admin_rights(
            bot=self.callback.bot,
            chat_id=group.tg_id,
            user_id=self.callback.from_user.id,
        )
        if is_user_admin is False:
            await self.callback.answer(
                "🚫Ты больше не админ в этой группе", show_alert=True
            )
            await delete_message(self.callback.message)
            return None
        group_info = await self.callback.bot.get_chat(group.tg_id)
        return await async_func(
            self,
            *args,
            callback_data=callback_data,
            groups_dao=groups_dao,
            title=f"«{group_info.title}»",
            **kwargs,
        )

    return wrapper


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
    @cant_write_to_user
    async def get_group_settings(self):
        await delete_message(self.message)
        groups_dao = GroupsDao(session=self.session)
        group_tg_id = self.message.chat.id
        group_schema = await groups_dao.get_group_settings(
            group_tg_id=TgIdSchema(tg_id=group_tg_id)
        )
        is_user_admin = await check_user_for_admin_rights(
            bot=self.message.bot,
            chat_id=group_tg_id,
            user_id=self.message.from_user.id,
        )
        chat_info = await self.message.bot.get_chat(group_tg_id)
        group_name = f"Настройки группы «{chat_info.title}»\n\n"
        if group_schema.is_there_settings is False:
            await self.message.bot.send_message(
                chat_id=self.message.from_user.id,
                text=group_name
                + make_build(
                    "В данной группе применяются настройки любого желающего,"
                    " если он начнёт регистрацию!"
                ),
            )
        else:
            banned_roles_text = RoleAttendant.get_banned_roles_text(
                roles_ids=group_schema.banned_roles
            )
            order_of_roles_text = RoleManager.get_current_order_text(
                selected_roles=group_schema.order_of_roles,
                to_save=False,
            )
            other_settings_text = make_build(
                f"Ночь длится (в секундах): {group_schema.time_for_night}\n"
                f"День длится (в секундах): {group_schema.time_for_day}\n"
            )
            await self.message.bot.send_message(
                chat_id=self.message.from_user.id,
                text=group_name + banned_roles_text,
            )
            await self.message.bot.send_message(
                chat_id=self.message.from_user.id,
                text=group_name + order_of_roles_text,
            )
            await self.message.bot.send_message(
                chat_id=self.message.from_user.id,
                text=group_name + other_settings_text,
            )
        if is_user_admin:
            await self.message.bot.send_message(
                chat_id=self.message.from_user.id,
                text=make_build(
                    f"❗️Ты можешь поменять настройки группы «{chat_info.title}» с помощью кнопок ниже:"
                ),
                reply_markup=set_up_group_kb(
                    group_id=group_schema.id,
                    is_there_settings=group_schema.is_there_settings,
                ),
            )

    @checking_for_ability_to_change_settings
    async def apply_any_settings(
        self,
        callback_data: GroupSettingsCbData,
        groups_dao: GroupsDao,
        title: str,
    ):
        await groups_dao.update(
            filters=IdSchema(id=callback_data.group_id),
            values=GroupSettingIdSchema(setting_id=None),
        )
        await self.callback.answer(
            f"✅Теперь в группе {title} "
            f"разрешены настройки всех желающих, если они начнут регистрацию!",
            show_alert=True,
        )
        await delete_message(self.callback.message)

    @checking_for_ability_to_change_settings
    async def apply_my_settings(
        self,
        callback_data: GroupSettingsCbData,
        groups_dao: GroupsDao,
        title: str,
    ):

        my_setting = await SettingsDao(
            session=self.session
        ).find_one_or_none(
            UserTgIdSchema(user_tg_id=self.callback.from_user.id)
        )

        await groups_dao.update(
            filters=IdSchema(id=callback_data.group_id),
            values=GroupSettingIdSchema(setting_id=my_setting.id),
        )
        await self.callback.answer(
            f"✅Теперь в группе {title} "
            f"применены твои настройки!",
            show_alert=True,
        )
        await delete_message(self.callback.message)
