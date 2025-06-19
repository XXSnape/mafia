from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.cb.cb_text import REFUSE_MOVE_CB
from services.game.processing_user_actions import UserManager

router = Router(name=__name__)


@router.callback_query(F.data == REFUSE_MOVE_CB)
async def refuse_movie(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_manager = UserManager(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await user_manager.refuse_movie()
