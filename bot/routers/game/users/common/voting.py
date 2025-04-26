from aiogram import Dispatcher, Router, F
from aiogram.exceptions import TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
    UserVoteIndexCbData,
)
from keyboards.inline.cb.cb_text import DONT_VOTE_FOR_ANYONE_CB
from services.game.processing_user_actions import UserManager

router = Router(name=__name__)


@router.callback_query(UserVoteIndexCbData.filter())
async def vote_for(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_manager = UserManager(
        callback=callback, state=state, dispatcher=dispatcher
    )
    try:
        await user_manager.vote_for(callback_data=callback_data)
    except TelegramRetryAfter:
        logger.exception("Ошибка при отправке сообщения")


@router.callback_query(F.data == DONT_VOTE_FOR_ANYONE_CB)
async def dont_vote_for_anyone(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_manager = UserManager(
        callback=callback, state=state, dispatcher=dispatcher
    )
    try:
        await user_manager.dont_vote_for_anyone()
    except TelegramRetryAfter:
        logger.exception("Ошибка при отправке сообщения")
