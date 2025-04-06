from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest

from cache.cache_types import PollBannedRolesCache, RolesLiteral
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.schemas.roles import ProhibitedRoleSchema
from database.schemas.common import UserTgId
from general.collection_of_roles import (
    get_data_with_roles,
    REQUIRED_ROLES,
)
from general.text import REQUIRE_TO_SAVE
from keyboards.inline.buttons.common import SAVE_BTN
from keyboards.inline.keypads.settings import (
    edit_roles_kb,
    suggest_banning_roles_kb,
)
from services.base import RouterHelper
from states.settings import SettingsFsm
from utils.tg import delete_message
from utils.pretty_text import make_build, make_pretty


class RoleAttendant(RouterHelper):

    @staticmethod
    def get_banned_roles_text(roles_ids: list[RolesLiteral]):
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
        user_filter = UserTgId(user_tg_id=user_id)
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
        await self.state.clear()
        dao = ProhibitedRolesDAO(session=self.session)
        user_filter = UserTgId(user_tg_id=self.callback.from_user.id)
        banned_roles_ids = await dao.get_roles_ids_of_banned_roles(
            user_filter
        )
        if banned_roles_ids:
            message = self.get_banned_roles_text(banned_roles_ids)
        else:
            message = make_build(
                "✅Все роли могут участвовать в игре!"
            )
        poll_data: PollBannedRolesCache = {
            "banned_roles_ids": banned_roles_ids
        }
        await self.state.set_state(SettingsFsm.BAN_ROLES)
        await self.state.set_data(poll_data)
        markup = edit_roles_kb(
            are_there_roles=bool(banned_roles_ids), to_ban=True
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
            UserTgId(user_tg_id=self.callback.from_user.id)
        )
        await self.callback.answer(
            "✅Теперь для игры доступны все роли!", show_alert=True
        )
        await self.view_banned_roles()

    async def suggest_roles_to_ban(self):
        poll_data: PollBannedRolesCache = await self.state.get_data()
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

    async def process_banned_roles(self):
        poll_data: PollBannedRolesCache = await self.state.get_data()
        banned_roles = poll_data["banned_roles_ids"]
        role_id: RolesLiteral = self.callback.data
        if role_id in banned_roles:
            banned_roles.remove(role_id)
        else:
            banned_roles.append(role_id)
        await self.state.set_data(poll_data)
        markup = suggest_banning_roles_kb(
            poll_data["banned_roles_ids"]
        )
        await self.callback.message.edit_reply_markup(
            reply_markup=markup,
        )

    async def save_prohibited_roles(self):
        poll_data: PollBannedRolesCache = await self.state.get_data()
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
