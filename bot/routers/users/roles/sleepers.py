from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from general.collection_of_roles import Roles
from keyboards.inline.callback_factory.recognize_user import UserActionIndexCbData
from services.actions_at_night import take_action_and_register_user
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.CLOFFELINE_GIRL_PUTS_TO_SLEEP,
    UserActionIndexCbData.filter(),
)
async def cloffeline_girl_puts_to_sleep(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    await take_action_and_register_user(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
        role=Roles.sleeper,
    )
