from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
    UserVoteIndexCbData,
)

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
    await user_manager.vote_for(callback_data=callback_data)
