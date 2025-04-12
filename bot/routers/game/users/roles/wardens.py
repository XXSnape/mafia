from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from services.game.saving_role_selection.warden import WardenSaver
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.SUPERVISOR_COLLECTS_INFORMATION, F.data.isdigit()
)
async def supervisor_collects_information(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = WardenSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.supervisor_collects_information()
