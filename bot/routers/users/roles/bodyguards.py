from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from general.collection_of_roles import Roles
from services.roles import GameCache, UserCache
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import (
    inform_players_and_trace_actions,
    take_action_and_register_user,
)
from states.states import UserFsm
from utils.utils import get_state_and_assign

router = Router(name=__name__)


@router.callback_query(
    UserFsm.BODYGUARD_PROTECTS, UserActionIndexCbData.filter()
)
async def bodyguard_protects(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    # user_data: UserCache = await state.get_data()
    # game_state = await get_state_and_assign(
    #     dispatcher=dispatcher,
    #     chat_id=user_data["game_chat"],
    #     bot_id=callback.bot.id,
    # )
    # game_data: GameCache = await game_state.get_data()
    # await callback.bot.send_message(
    #     chat_id=user_data["game_chat"],
    #     text="Кто-то пожертвовал собой!",
    # )
    await take_action_and_register_user(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
        # message_to_group="Кто-то пожертвовал собой!",
        # message_to_user="Ты выбрал пожертвовать собой, чтобы спасти {url}",
        role=Roles.bodyguard,
        # last_processed_user_key="last_self_protected",
        # list_to_process_key="self_protected",
    )
    # game_state, game_data, protected_user_id = (
    #     await get_user_id_and_inform_players(
    #         callback=callback,
    #         callback_data=callback_data,
    #         state=state,
    #         dispatcher=dispatcher,
    #         message_to_group="Кто-то пожертвовал собой!",
    #         message_to_user="Ты выбрал пожертвовать собой, чтобы спасти {url}",
    #     )
    # )
    # game_data["last_self_protected"] = protected_user_id
    # game_data["self_protected"].append(protected_user_id)
    # await game_state.set_data(game_data)
