from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from cache.cache_types import PollBannedRolesCache, RolesLiteral
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.schemas.common import UserTgIdSchema
from database.schemas.roles import ProhibitedRoleSchema
from general.collection_of_roles import (
    REQUIRED_ROLES,
    get_data_with_roles,
)
from general.text import REQUIRE_TO_SAVE
from keyboards.inline.callback_factory.help import BannedRolesCbData
from keyboards.inline.keypads.banned_roles import (
    edit_banned_roles_kb,
    suggest_banning_roles_kb,
)
from services.base import RouterHelper
from utils.pretty_text import make_build
from utils.tg import delete_message


class RoleAttendant(RouterHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = "poll_banned_roles"

    @staticmethod
    def get_banned_roles_text(roles_ids: list[RolesLiteral]):
        if not roles_ids:
            return make_build("✅Все роли могут участвовать в игре!")
        result = "🚫Забаненные роли:\n\n"
        all_roles = get_data_with_roles()
        for num, role_id in enumerate(roles_ids, 1):
            result += (
                f"{num}) {all_roles[role_id].role}"
                f"{all_roles[role_id].grouping.value.name[-1]}\n"
            )
        return make_build(result)

    async def _save_new_prohibited_roles(
        self, roles_ids: list[RolesLiteral]
    ):
        group_schema = await self.get_group_id_schema()
        prohibited_dao = ProhibitedRolesDAO(session=self.session)
        await prohibited_dao.delete(group_schema)
        prohibited_roles = [
            ProhibitedRoleSchema(
                group_id=group_schema.group_id, role_id=role_id
            )
            for role_id in roles_ids
        ]
        await prohibited_dao.add_many(prohibited_roles)
        order_of_roles_dao = OrderOfRolesDAO(session=self.session)
        used_roles = set(
            await order_of_roles_dao.get_roles_ids_of_order_of_roles(
                group_schema
            )
        )
        if used_roles - set(roles_ids) != used_roles:
            await order_of_roles_dao.delete(group_schema)
            await self.callback.message.answer(
                text=make_build(
                    "❗️❗️❗️ВНИМАНИЕ! ЗАБАНЕННЫЕ РОЛИ ЕСТЬ В СПИСКЕ С ПОРЯДКОМ РОЛЕЙ. "
                    "Порядок ролей очищен, исправь это при необходимости"
                ),
            )
            return True
        return False

    async def ban_everything(self):
        all_roles = get_data_with_roles()
        roles_ids = list(set(all_roles.keys()) - set(REQUIRED_ROLES))
        has_order_been_reset = await self._save_new_prohibited_roles(
            roles_ids=roles_ids
        )
        await self.callback.answer(
            "✅Ты успешно забанил все опциональные роли!",
            show_alert=True,
        )
        await self.view_banned_roles(
            has_order_been_reset=has_order_been_reset
        )

    async def view_banned_roles(
        self, has_order_been_reset: bool = False
    ):
        group_schema = await self.get_group_id_schema()
        await self.clear_settings_data()
        dao = ProhibitedRolesDAO(session=self.session)
        banned_roles_ids = await dao.get_roles_ids_of_banned_roles(
            group_schema
        )
        message = self.get_banned_roles_text(banned_roles_ids)
        poll_data = PollBannedRolesCache(
            banned_roles_ids=banned_roles_ids
        )
        await self.set_settings_data(poll_data)
        markup = edit_banned_roles_kb(
            banned_roles_ids=banned_roles_ids
        )
        if has_order_been_reset:
            await delete_message(self.callback.message)
            await self.callback.message.answer(
                text=message,
                reply_markup=markup,
            )
        else:
            with suppress(TelegramAPIError):
                await self.callback.message.edit_text(
                    text=message,
                    reply_markup=markup,
                )

    async def clear_banned_roles(self):
        dao = ProhibitedRolesDAO(session=self.session)
        group_schema = await self.get_group_id_schema()
        await dao.delete(group_schema)
        await self.callback.answer(
            "✅Теперь для игры доступны все роли!", show_alert=True
        )
        await self.view_banned_roles()

    async def suggest_roles_to_ban(self):
        poll_data: PollBannedRolesCache = (
            await self.get_settings_data()
        )
        markup = suggest_banning_roles_kb(
            poll_data["banned_roles_ids"]
        )
        text = (
            "Выбери роли, которые нужно забанить.\n"
            "✅ - роль не забанена\n"
            "🚫 - роль уже забанена\n\n" + REQUIRE_TO_SAVE
        )
        await self.callback.message.edit_text(
            make_build(text),
            reply_markup=markup,
        )

    async def process_banned_roles(
        self, callback_data: BannedRolesCbData
    ):
        poll_data: PollBannedRolesCache = (
            await self.get_settings_data()
        )
        banned_roles = poll_data["banned_roles_ids"]
        role_id: RolesLiteral = callback_data.role_id
        if role_id in banned_roles:
            banned_roles.remove(role_id)
        else:
            banned_roles.append(role_id)
        await self.set_settings_data(poll_data)
        markup = suggest_banning_roles_kb(
            poll_data["banned_roles_ids"]
        )
        await self.callback.message.edit_reply_markup(
            reply_markup=markup,
        )

    async def save_prohibited_roles(self):
        poll_data: PollBannedRolesCache = (
            await self.get_settings_data()
        )
        banned_roles = poll_data["banned_roles_ids"]
        has_order_been_reset = await self._save_new_prohibited_roles(
            roles_ids=banned_roles
        )
        await self.callback.answer(
            "✅Ты успешно забанил роли!", show_alert=True
        )
        await self.view_banned_roles(
            has_order_been_reset=has_order_been_reset
        )
