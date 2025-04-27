from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
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
    suggest_banning_roles_kb,
    edit_banned_roles_kb,
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
        user_id = self.callback.from_user.id
        user_filter = UserTgIdSchema(user_tg_id=user_id)
        prohibited_dao = ProhibitedRolesDAO(session=self.session)
        await prohibited_dao.delete(user_filter)
        prohibited_roles = [
            ProhibitedRoleSchema(user_tg_id=user_id, role_id=role_id)
            for role_id in roles_ids
        ]
        await prohibited_dao.add_many(prohibited_roles)
        order_of_roles_dao = OrderOfRolesDAO(session=self.session)
        used_roles = set(
            await order_of_roles_dao.get_roles_ids_of_order_of_roles(
                user_filter
            )
        )
        if used_roles - set(roles_ids) != used_roles:
            await order_of_roles_dao.delete(user_filter)
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
            "✅Вы успешно забанили все опциональные роли!",
            show_alert=True,
        )
        await self.view_banned_roles(
            has_order_been_reset=has_order_been_reset
        )

    async def view_banned_roles(
        self, has_order_been_reset: bool = False
    ):
        await self.clear_settings_data()
        dao = ProhibitedRolesDAO(session=self.session)
        user_filter = UserTgIdSchema(
            user_tg_id=self.callback.from_user.id
        )
        banned_roles_ids = await dao.get_roles_ids_of_banned_roles(
            user_filter
        )
        message = self.get_banned_roles_text(banned_roles_ids)
        poll_data: PollBannedRolesCache = {
            "banned_roles_ids": banned_roles_ids
        }
        await self.set_settings_data(poll_data)
        markup = edit_banned_roles_kb(
            are_there_roles=bool(banned_roles_ids)
        )
        if has_order_been_reset:
            await delete_message(self.callback.message)
            await self.callback.message.answer(
                text=message,
                reply_markup=markup,
            )
        else:
            with suppress(TelegramBadRequest):
                await self.callback.message.edit_text(
                    text=message,
                    reply_markup=markup,
                )

    async def clear_banned_roles(self):
        dao = ProhibitedRolesDAO(session=self.session)
        await dao.delete(
            UserTgIdSchema(user_tg_id=self.callback.from_user.id)
        )
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
            "✅Вы успешно забанили роли!", show_alert=True
        )
        await self.view_banned_roles(
            has_order_been_reset=has_order_been_reset
        )
