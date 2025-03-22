from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest

from cache.cache_types import PollBannedRolesCache
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.schemas.roles import UserTgId, ProhibitedRoleSchema
from keyboards.inline.keypads.settings import (
    edit_roles_kb,
    go_to_following_roles_kb,
)
from services.settings.base import RouterHelper
from states.settings import SettingsFsm
from utils.roles import get_roles_without_bases
from utils.tg import delete_message
from utils.utils import make_build


class RoleAttendant(RouterHelper):

    @staticmethod
    def _get_banned_roles_text(roles: list[str]):
        result = make_build("🚫Забаненные роли:\n\n")
        for num, role in enumerate(roles, 1):
            result += f"{num}) {role}\n"
        return result

    async def _save_new_prohibited_roles(self, roles: list[str]):
        user_id = self._get_user_id()
        bot = self._get_bot()
        prohibited_dao = ProhibitedRolesDAO(session=self.session)
        await prohibited_dao.delete(UserTgId(user_tg_id=user_id))
        prohibited_roles = [
            ProhibitedRoleSchema(user_tg_id=user_id, role=role)
            for role in roles
        ]
        await prohibited_dao.add_many(prohibited_roles)
        order_of_roles_dao = OrderOfRolesDAO(session=self.session)
        used_roles = set(
            record.role
            for record in await order_of_roles_dao.find_all(
                UserTgId(user_tg_id=user_id)
            )
        )
        if used_roles - set(roles) != used_roles:
            await order_of_roles_dao.delete(
                UserTgId(user_tg_id=user_id)
            )
            await bot.send_message(
                chat_id=user_id,
                text=make_build(
                    "❗️❗️❗️ВНИМАНИЕ! ЗАБАНЕННЫЕ РОЛИ ЕСТЬ В СПИСКЕ С ПОРЯДКОМ РОЛЕЙ. "
                    "Порядок ролей очищен, исправь это при необходимости"
                ),
            )

    async def _send_poll_and_save_data(
        self,
        available_roles,
        current_number: int,
        max_number: int,
        banned_roles: list,
    ):
        bot = (
            self.poll_answer.bot
            if self.poll_answer
            else self.callback.bot
        )
        user_id = self._get_user_id()
        question = make_build("Какие роли хочешь забанить? ")
        if banned_roles:
            question += make_build(
                "Уже выбранные в сообщении выше⏫"
            )
        poll = await bot.send_poll(
            chat_id=user_id,
            question=question,
            options=available_roles,
            allows_multiple_answers=True,
            reply_markup=go_to_following_roles_kb(
                current_number=current_number,
                max_number=max_number,
                are_there_roles=bool(banned_roles),
            ),
            is_anonymous=False,
        )
        poll_data: PollBannedRolesCache = {
            "number": current_number,
            "banned_roles": banned_roles,
            "poll_id": poll.message_id,
        }
        await self.state.update_data(poll_data)

    async def view_banned_roles(
        self,
    ):
        poll_data: PollBannedRolesCache = await self.state.get_data()
        await self._delete_last_message(poll_data)
        banned_roles = await self._get_banned_roles()
        if banned_roles:
            message = self._get_banned_roles_text(banned_roles)
        else:
            message = make_build(
                "✅Все роли могут участвовать в игре!"
            )
        await self.state.clear()
        await self.state.set_state(SettingsFsm.BAN_ROLES)
        if self.callback:
            await delete_message(message=self.callback.message)
        bot = self._get_bot()
        user_id = self._get_user_id()
        await bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=edit_roles_kb(
                are_there_roles=bool(banned_roles)
            ),
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
        current_number = 0
        available_roles, max_number = get_roles_without_bases(
            number=current_number
        )
        await self.callback.message.delete()
        await self._send_poll_and_save_data(
            available_roles=available_roles,
            current_number=current_number,
            max_number=max_number,
            banned_roles=[],
        )

    async def process_banned_roles(self):
        poll_data: PollBannedRolesCache = await self.state.get_data()
        await self._delete_last_message(poll_data)
        current_number = poll_data["number"]
        available_roles, max_number = get_roles_without_bases(
            number=current_number
        )
        banned_roles = poll_data["banned_roles"]
        ids = self.poll_answer.option_ids
        for role_id in ids:
            role_name = available_roles[role_id]
            if role_name not in banned_roles:
                banned_roles.append(role_name)
        await self.poll_answer.bot.delete_message(
            chat_id=self.poll_answer.user.id,
            message_id=poll_data["poll_id"],
        )
        if current_number + 1 > max_number:
            await self._save_new_prohibited_roles(roles=banned_roles)
            await self.view_banned_roles()
            return
        text = self._get_banned_roles_text(banned_roles)
        msg = await self.poll_answer.bot.send_message(
            chat_id=self.poll_answer.user.id,
            text=self.REQUIRE_TO_SAVE + text,
        )
        await self.state.update_data({"last_msg_id": msg.message_id})
        current_number += 1
        available_roles, max_number = get_roles_without_bases(
            number=current_number
        )
        await self._send_poll_and_save_data(
            available_roles=available_roles,
            current_number=current_number,
            max_number=max_number,
            banned_roles=banned_roles,
        )

    async def switch_poll(self):
        poll_data: PollBannedRolesCache = await self.state.get_data()
        banned_roles = poll_data["banned_roles"]
        current_number = int(self.callback.data)
        available_roles, max_number = get_roles_without_bases(
            number=current_number
        )
        await self.callback.message.delete()
        await self._send_poll_and_save_data(
            available_roles=available_roles,
            current_number=current_number,
            max_number=max_number,
            banned_roles=banned_roles,
        )

    async def _delete_last_message(
        self, poll_data: PollBannedRolesCache
    ):
        last_msg_id = poll_data.get("last_msg_id")
        if last_msg_id:
            bot = self._get_bot()
            user_id = self._get_user_id()
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=user_id,
                    message_id=last_msg_id,
                )

    async def save_prohibited_roles(self):
        poll_data: PollBannedRolesCache = await self.state.get_data()
        await self._delete_last_message(poll_data)
        banned_roles = poll_data["banned_roles"]
        await self._save_new_prohibited_roles(roles=banned_roles)
        await self.callback.answer(
            "✅Вы успешно забанили роли!", show_alert=True
        )
        await self.view_banned_roles()
