from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from cache.cache_types import GameCache, UserCache
from general.collection_of_roles import Roles
from keyboards.inline.cb.cb_text import DRAW_CB
from services.actions_at_night import get_game_state_and_data
from services.roles import Analyst
from states.states import UserFsm
from utils.utils import get_state_and_assign

router = Router(name=__name__)


@router.callback_query(UserFsm.ANALYST_ASSUMES, F.data == DRAW_CB)
async def analyst_assumes_draw(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    _, game_data = await get_game_state_and_data(
        callback=callback,
        state=state,
        dispatcher=dispatcher,
    )
    game_data[Analyst.processed_users_key].append(0)
    await callback.message.delete()
    await callback.message.answer(
        text="Ты предположил, что никого не повесят днём"
    )
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=Analyst.message_to_group_after_action,
    )
