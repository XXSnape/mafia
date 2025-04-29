from aiogram import Dispatcher, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.cb.cb_text import CANCEL_CB, CANCEL_BET_CB
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from services.game.registartion import Registration
from sqlalchemy.ext.asyncio import AsyncSession
from states.game import GameFsm

router = Router(name=__name__)
router.message.middleware(DatabaseMiddlewareWithCommit())
router.message.middleware(DatabaseMiddlewareWithoutCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())


@router.message(
    CommandStart(deep_link=True),
)
async def join_to_game(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    dispatcher: Dispatcher,
    session_with_commit: AsyncSession,
    scheduler: AsyncIOScheduler,
    broker: RabbitBroker,
):
    registration = Registration(
        message=message,
        state=state,
        dispatcher=dispatcher,
        session=session_with_commit,
        scheduler=scheduler,
        broker=broker,
    )
    await registration.join_to_game(command=command)


@router.callback_query(
    GameFsm.WAIT_FOR_STARTING_GAME, F.data == CANCEL_BET_CB
)
async def cancel_bet(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
    dispatcher: Dispatcher,
):
    registration = Registration(
        callback=callback,
        state=state,
        session=session_without_commit,
        dispatcher=dispatcher,
    )
    await registration.cancel_bet()


@router.callback_query(
    GameFsm.WAIT_FOR_STARTING_GAME,
    F.data.in_(get_data_with_roles().keys()),
)
async def request_money(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    registration = Registration(
        callback=callback,
        state=state,
        session=session_without_commit,
    )
    await registration.request_money()


@router.message(
    GameFsm.WAIT_FOR_STARTING_GAME, F.text.regexp(r"^[1-9]\d*$")
)
async def set_bet(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
    session_without_commit: AsyncSession,
):
    registration = Registration(
        message=message,
        state=state,
        dispatcher=dispatcher,
        session=session_without_commit,
    )
    await registration.set_bet()


@router.message(GameFsm.WAIT_FOR_STARTING_GAME)
async def delete_erroneous_message(message: Message):
    await message.delete()
