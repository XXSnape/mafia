from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from general.collection_of_roles import Roles
from keyboards.inline.callback_factory.recognize_user import UserActionIndexCbData
from services.actions_at_night import take_action_and_register_user
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.INSTIGATOR_LYING, UserActionIndexCbData.filter()
)
async def instigator_lying(
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
        # message_to_group="Кажется, кто-то становится жертвой психологического насилия!",
        # message_to_user="Ты выбрал прополоскать мозги {url}",
        role=Roles.instigator,
        # list_to_process_key="missed",
        # last_processed_user_key=None,
    )
