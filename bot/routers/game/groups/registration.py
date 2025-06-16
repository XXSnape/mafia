from aiogram import Dispatcher, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker

from general.commands import GroupCommands
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
)
from services.game.registartion import (
    Registration,
)
from sqlalchemy.ext.asyncio import AsyncSession
from states.game import GameFsm

router = Router(name=__name__)


@router.message(
    Command(GroupCommands.registration.name),
    StateFilter(default_state),
)
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


@router.message(
    GameFsm.REGISTRATION, Command(GroupCommands.extend.name)
)
async def extend_registration(
    message: Message, state: FSMContext, scheduler: AsyncIOScheduler
):
    registration = Registration(
        message=message, state=state, scheduler=scheduler
    )
    await registration.extend_registration()


@router.message(
    GameFsm.REGISTRATION, Command(GroupCommands.revoke.name)
)
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


@router.message(
    GameFsm.REGISTRATION, Command(GroupCommands.game.name)
)
async def finish_registration_and_start_game(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
    scheduler: AsyncIOScheduler,
    broker: RabbitBroker,
    session_with_commit: AsyncSession,
):
    registration = Registration(
        message=message,
        state=state,
        dispatcher=dispatcher,
        scheduler=scheduler,
        broker=broker,
        session=session_with_commit,
    )
    await registration.finish_registration_and_start_game()


@router.message(
    GameFsm.REGISTRATION, Command(GroupCommands.leave.name)
)
async def leave_game(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    registration = Registration(
        message=message, state=state, dispatcher=dispatcher
    )
    await registration.leave_game()
