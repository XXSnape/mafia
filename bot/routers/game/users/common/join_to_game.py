from aiogram import Router, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline.cb.cb_text import CANCEL_CB
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from services.game.registartion import Registration
from states.states import GameFsm

router = Router(name=__name__)
router.message.middleware(DatabaseMiddlewareWithCommit())
router.message.middleware(DatabaseMiddlewareWithoutCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())


@router.message(CommandStart(deep_link=True))
async def join_to_game(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    dispatcher: Dispatcher,
    session_with_commit: AsyncSession,
):
    registration = Registration(
        message=message,
        state=state,
        dispatcher=dispatcher,
        session=session_with_commit,
    )
    await registration.join_to_game(command=command)


@router.callback_query(
    GameFsm.WAIT_FOR_STARTING_GAME, F.data == CANCEL_CB
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


@router.callback_query(GameFsm.WAIT_FOR_STARTING_GAME)
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


@router.message(F.text.regexp(r"[1-9]\d*"))
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
