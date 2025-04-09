from dataclasses import dataclass

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.schemas.common import UserTgIdSchema
from utils.pretty_text import make_build


@dataclass
class RouterHelper:
    callback: CallbackQuery | None = None
    state: FSMContext | None = None
    session: AsyncSession | None = None
    message: Message | None = None
    dispatcher: Dispatcher | None = None
    scheduler: AsyncIOScheduler | None = None
    broker: RabbitBroker | None = None

    def _get_user_id(self):
        obj = self.callback or self.message
        return obj.from_user.id

    def _get_bot(self):
        obj = self.callback or self.message
        return obj.bot
