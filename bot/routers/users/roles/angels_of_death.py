from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from general.collection_of_roles import Roles
from keyboards.inline.callback_factory.recognize_user import UserActionIndexCbData
from services.actions_at_night import take_action_and_register_user
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.ANGEL_TAKES_REVENGE, UserActionIndexCbData.filter()
)
async def angel_takes_revenge(
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
        role=Roles.angel_of_death,
        # message_to_group="Ангел смерти спускается во имя мести!",
        # message_to_user="Ты выбрал отомстить {url}",
    )
    # game_state, game_data, died_user_id = (
    #     await get_user_id_and_inform_players(
    #         callback=callback,
    #         callback_data=callback_data,
    #         state=state,
    #         dispatcher=dispatcher,
    #         message_to_group="Ангел смерти спускается во имя мести!",
    #         message_to_user="Ты выбрал отомстить {url}",
    #     )
    # )
    # game_data["killed_by_angel_of_death"].append(died_user_id)
