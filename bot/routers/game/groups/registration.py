from aiogram import Dispatcher, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker
from keyboards.inline.cb.cb_text import (
    FINISH_REGISTRATION_CB,
)
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
)
from services.game.registartion import (
    Registration,
)
from sqlalchemy.ext.asyncio import AsyncSession
from states.states import GameFsm

router = Router(name=__name__)
router.message.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithCommit())


@router.message(Command("registration"), StateFilter(default_state))
async def start_registration(
    message: Message,
    state: FSMContext,
    session_with_commit: AsyncSession,
    scheduler: AsyncIOScheduler,
    dispatcher: Dispatcher,
    broker: RabbitBroker,
):
    registration = Registration(
        message=message,
        state=state,
        session=session_with_commit,
        dispatcher=dispatcher,
        scheduler=scheduler,
        broker=broker,
    )
    await registration.start_registration()


@router.message(GameFsm.REGISTRATION, Command("extend"))
async def extend_registration(
    message: Message, state: FSMContext, scheduler: AsyncIOScheduler
):
    registration = Registration(
        message=message, state=state, scheduler=scheduler
    )
    await registration.extend_registration()


@router.message(GameFsm.REGISTRATION, Command("revoke"))
async def cancel_game(
    message: Message,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
    dispatcher: Dispatcher,
):
    registration = Registration(
        message=message,
        state=state,
        scheduler=scheduler,
        dispatcher=dispatcher,
    )
    await registration.cancel_game()


@router.callback_query(
    GameFsm.REGISTRATION, F.data == FINISH_REGISTRATION_CB
)
async def finish_registration(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
    scheduler: AsyncIOScheduler,
    broker: RabbitBroker,
    session_with_commit: AsyncSession,
):
    registration = Registration(
        callback=callback,
        state=state,
        dispatcher=dispatcher,
        scheduler=scheduler,
        broker=broker,
        session=session_with_commit,
    )
    await registration.finish_registration()
