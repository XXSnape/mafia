from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.cb.cb_text import DRAW_CB
from services.game.saving_role_selection.analyst import AnalystSaver

router = Router(name=__name__)


@router.callback_query(F.data == DRAW_CB)
async def analyst_assumes_draw(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = AnalystSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.analyst_assumes_draw()
