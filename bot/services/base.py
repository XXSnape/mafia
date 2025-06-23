from dataclasses import dataclass
from typing import TypedDict

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.cache_types import PersonalSettingsCache, AllSettingsCache
from database.dao.groups import GroupsDao
from database.schemas.common import TgIdSchema, IdSchema
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas.groups import GroupIdSchema


@dataclass
class RouterHelper:
    callback: CallbackQuery | None = None
    state: FSMContext | None = None
    session: AsyncSession | None = None
    message: Message | None = None
    dispatcher: Dispatcher | None = None
    scheduler: AsyncIOScheduler | None = None
    broker: RabbitBroker | None = None
    key: str | None = None

    def _get_user_id(self):
        obj = self.callback or self.message
        return obj.from_user.id

    def _get_bot(self):
        obj = self.callback or self.message
        return obj.bot

    async def clear_settings_data(self):
        data: PersonalSettingsCache = await self.state.get_data()
        data["settings"] = AllSettingsCache(
            group_id=data["settings"]["group_id"]
        )
        await self.state.set_data(data)

    async def get_group_id_schema(self):
        data: PersonalSettingsCache = await self.state.get_data()
        return GroupIdSchema(group_id=data["settings"]["group_id"])

    async def set_settings_data(self, data: dict):
        user_data: PersonalSettingsCache = (
            await self.state.get_data()
        )
        user_data["settings"][self.key] = data
        await self.state.set_data(user_data)

    async def get_settings_data(self):
        settings: PersonalSettingsCache = await self.state.get_data()
        return settings["settings"][self.key]

    async def get_group_or_create(self):
        groups_dao = GroupsDao(session=self.session)
        group_schema = TgIdSchema(tg_id=self.message.chat.id)
        group = await groups_dao.find_one_or_none(
            TgIdSchema(tg_id=self.message.chat.id)
        )
        if group is None:
            group = await groups_dao.add(group_schema)
        return group
