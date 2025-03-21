from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.schemas.roles import UserTgId, ProhibitedRoleSchema
from keyboards.inline.keypads.settings import (
    edit_roles_kb,
    select_setting_kb,
    go_to_following_roles_kb,
)
from services.settings.base import RouterHelper
from states.settings import SettingsFsm
from utils.roles import get_roles_without_bases
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
        dao = ProhibitedRolesDAO(session=self.session)
        await dao.delete(UserTgId(user_tg_id=user_id))
        prohibited_roles = [
            ProhibitedRoleSchema(user_tg_id=user_id, role=role)
            for role in roles
        ]
        await dao.add_many(prohibited_roles)

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
        await self.state.update_data(
            {
                "number": current_number,
                "banned_roles": banned_roles,
                "poll_id": poll.message_id,
            }
        )

    async def view_banned_roles(
        self,
    ):
        banned_roles = await self._get_banned_roles()
        if banned_roles:
            message = self._get_banned_roles_text(banned_roles)
        else:
            message = make_build(
                "✅Все роли могут участвовать в игре!"
            )
        await self.state.set_state(SettingsFsm.BAN_ROLES)
        await self.callback.message.delete()
        await self.callback.message.answer(
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
        pool_data = await self.state.get_data()
        await self._delete_last_message(pool_data)
        current_number = pool_data["number"]
        available_roles, max_number = get_roles_without_bases(
            number=current_number
        )
        banned_roles = pool_data["banned_roles"]
        ids = self.poll_answer.option_ids
        for role_id in ids:
            role_name = available_roles[role_id]
            if role_name not in banned_roles:
                banned_roles.append(role_name)
        await self.poll_answer.bot.delete_message(
            chat_id=self.poll_answer.user.id,
            message_id=pool_data["poll_id"],
        )
        if current_number + 1 > max_number:
            await self._save_new_prohibited_roles(roles=banned_roles)
            await self.view_banned_roles()
            return
        text = self._get_banned_roles_text(banned_roles)
        msg = await self.poll_answer.bot.send_message(
            chat_id=self.poll_answer.user.id,
            text=make_build(
                "❗️Чтобы сохранить изменения, нажмите «Сохранить💾»\n\n"
            )
            + text,
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
        poll_data = await self.state.get_data()
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

    async def _delete_last_message(self, pool_data):
        last_msg_id = pool_data.get("last_msg_id")
        if last_msg_id:
            bot = self._get_bot()
            user_id = self._get_user_id()
            await bot.delete_message(
                chat_id=user_id,
                message_id=last_msg_id,
            )

    async def save_prohibited_roles(self):
        pool_data = await self.state.get_data()
        await self._delete_last_message(pool_data)
        banned_roles = pool_data["banned_roles"]
        await self._save_new_prohibited_roles(roles=banned_roles)
        await self.callback.answer(
            "✅Вы успешно забанили роли!", show_alert=True
        )
        await self.view_banned_roles()
