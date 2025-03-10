from contextlib import suppress

from aiogram import Dispatcher, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatPermissions
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import take_action_and_register_user
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.PROSECUTOR_ARRESTS, UserActionIndexCbData.filter()
)
async def prosecutor_arrests(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    game_data, arrested_user_id = (
        await take_action_and_register_user(
            callback=callback,
            callback_data=callback_data,
            state=state,
            dispatcher=dispatcher,
        )
    )
    with suppress(TelegramBadRequest):
        await callback.bot.restrict_chat_member(
            chat_id=game_data["game_chat"],
            user_id=arrested_user_id,
            permissions=ChatPermissions(can_send_messages=False),
        )
