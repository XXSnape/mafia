from aiogram import Bot
from aiogram.types import ChatMemberUpdated
from database.dao.groups import GroupsDao
from database.schemas.common import TgIdSchema
from general.commands import PrivateCommands, GroupCommands
from general.text import REQUIRED_PERMISSIONS
from services.base import RouterHelper
from utils.pretty_text import make_build


class AddingRouter(RouterHelper):
    async def adding_to_group(
        self, event: ChatMemberUpdated, bot: Bot
    ):
        chat_info = await bot.get_chat(event.chat.id)
        group_dao = GroupsDao(session=self.session)
        await group_dao.add(values=TgIdSchema(tg_id=event.chat.id))
        if chat_info.permissions.can_send_messages:
            text = (
                "Привет! Чтобы запустить игру, выдайте боту "
                "следующие права и введите "
                f"/{GroupCommands.registration.name}:\n\n{REQUIRED_PERMISSIONS}\n\n"
                f"Чтобы узнать подробности о правилах, "
                f"напишите /{PrivateCommands.help.name} боту в личные сообщения!"
            )
            await event.answer(text=make_build(text))

    async def group_to_supergroup_migration(self):
        group_dao = GroupsDao(session=self.session)
        await group_dao.update(
            filters=TgIdSchema(tg_id=self.message.chat.id),
            values=TgIdSchema(tg_id=self.message.migrate_to_chat_id),
        )
