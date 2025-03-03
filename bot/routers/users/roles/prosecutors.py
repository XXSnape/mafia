from contextlib import suppress

from aiogram import Router, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatPermissions

from cache.cache_types import UserCache, GameCache
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)

from states.states import UserFsm
from utils.utils import get_state_and_assign

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
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    await callback.bot.send_message(
        chat_id=user_data["game_chat"],
        text="По данным разведки потенциальный злоумышленник арестован!",
    )
    arrested_user_id = game_data["players_ids"][
        callback_data.user_index
    ]
    with suppress(TelegramBadRequest):
        await callback.bot.restrict_chat_member(
            chat_id=game_data["game_chat"],
            user_id=arrested_user_id,
            permissions=ChatPermissions(can_send_messages=False),
        )
    game_data["cant_vote"].append(arrested_user_id)
    game_data["last_arrested"] = arrested_user_id
    url = game_data["players"][str(arrested_user_id)]["url"]
    await callback.message.delete()
    await callback.message.answer(f"Ты выбрал арестовать {url}")
    await game_state.set_data(game_data)
