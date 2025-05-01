from dataclasses import dataclass

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.cache_types import PersonalSettingsCache
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession


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
        data["settings"] = {}
        await self.state.set_data(data)

    async def set_settings_data(self, data: dict):
        user_data: PersonalSettingsCache = (
            await self.state.get_data()
        )
        user_data["settings"][self.key] = data
        await self.state.set_data(user_data)

    async def get_settings_data(self):
        settings: PersonalSettingsCache = await self.state.get_data()
        return settings["settings"][self.key]
