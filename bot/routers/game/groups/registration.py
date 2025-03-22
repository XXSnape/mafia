from aiogram import Dispatcher, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline.cb.cb_text import (
    FINISH_REGISTRATION_CB,
)
from middlewares.db import (
    DatabaseMiddlewareWithoutCommit,
)
from services.game.registartion import (
    Registration,
)
from states.states import GameFsm

router = Router(name=__name__)
router.message.middleware(DatabaseMiddlewareWithoutCommit())


@router.message(Command("registration"), StateFilter(default_state))
async def start_registration(
    message: Message,
    state: FSMContext,
    session_without_commit: AsyncSession,
    scheduler: AsyncIOScheduler,
):
    registration = Registration(
        message=message, state=state, session=session_without_commit
    )
    await registration.start_registration()


@router.callback_query(
    GameFsm.REGISTRATION, F.data == FINISH_REGISTRATION_CB
)
async def finish_registration(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    registration = Registration(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await registration.finish_registration()
