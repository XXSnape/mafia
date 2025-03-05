from aiogram import Router, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import UserCache, GameCache, Roles
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import (
    get_user_id_and_inform_players,
    take_action_and_register_user,
)
from states.states import UserFsm
from utils.utils import get_state_and_assign

router = Router(name=__name__)


@router.callback_query(
    UserFsm.MAFIA_ATTACKS, UserActionIndexCbData.filter()
)
async def mafia_attacks(
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
        # message_to_group="Мафия выбрала жертву!",
        # message_to_user="Ты выбрал убить {url}",
        role=Roles.don,
    )
    # game_state, game_data, died_user_id = (
    #     await get_user_id_and_inform_players(
    #         callback=callback,
    #         callback_data=callback_data,
    #         state=state,
    #         dispatcher=dispatcher,
    #         message_to_group="Мафия выбрала жертву!",
    #         message_to_user="Ты выбрал убить {url}",
    #     )
    # )
    # user_data: UserCache = await state.get_data()
    # game_state = await get_state_and_assign(
    #     dispatcher=dispatcher,
    #     chat_id=user_data["game_chat"],
    #     bot_id=callback.bot.id,
    # )
    # game_data: GameCache = await game_state.get_data()
    # await callback.bot.send_message(
    #     chat_id=user_data["game_chat"], text="Мафия выбрала жертву!"
    # )
    # died_user_id = game_data["players_ids"][callback_data.user_index]
    # # await callback.bot.send_message(
    # #     chat_id=died_user_id,
    # #     text="Мафия уже рядом, тебе поможет только чудо",
    # # )
    # game_data["died"].append(died_user_id)
    # url = game_data["players"][str(died_user_id)]["url"]
    # await callback.message.delete()
    # await callback.message.answer(f"Ты выбрал убить {url}")
