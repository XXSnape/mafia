import asyncio

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from constants.output import NUMBER_OF_NIGHT
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import (
    get_game_state_data_and_user_id,
    trace_all_actions,
    save_notification_message,
)
from services.roles import Mafia, Traitor
from states.states import UserFsm
from utils.utils import make_pretty

router = Router(name=__name__)


@router.callback_query(
    UserFsm.TRAITOR_FINDS_OUT,
    UserActionIndexCbData.filter(),
)
async def traitor_finds_out(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    _, game_data, user_id = await get_game_state_data_and_user_id(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
    )
    url = game_data["players"][str(user_id)]["url"]
    role = game_data["players"][str(user_id)]["pretty_role"]
    await callback.message.delete()
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=Traitor.message_to_group_after_action,
    )
    await callback.message.answer(
        text=Traitor.message_to_user_after_action.format(url=url)
    )
    trace_all_actions(
        callback=callback, game_data=game_data, user_id=user_id
    )
    save_notification_message(
        game_data=game_data,
        processed_user_id=user_id,
        message=Traitor.notification_message,
        current_user_id=callback.from_user.id,
    )
    await asyncio.gather(
        *(
            callback.bot.send_message(
                chat_id=player_id,
                text=NUMBER_OF_NIGHT.format(
                    game_data["number_of_night"]
                )
                + f"{make_pretty(Traitor.role)} проверил и узнал, что {url} - {role}",
            )
            for player_id in game_data[Mafia.roles_key]
            + game_data[Traitor.roles_key]
        )
    )
