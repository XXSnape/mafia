from aiogram import Dispatcher, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import GameCache
from constants.output import NUMBER_OF_NIGHT, ROLE_IS_KNOWN
from keyboards.inline.keypads.mailing import selection_to_warden_kb
from services.game.actions_at_night import (
    get_game_state_and_data,
    trace_all_actions,
    save_notification_message,
)
from services.game.roles.warden import Warden
from states.states import UserFsm
from utils.tg import delete_message

router = Router(name=__name__)


async def generate_markup_after_selection(
    callback: CallbackQuery,
    game_state: FSMContext,
    game_data: GameCache,
):
    markup = selection_to_warden_kb(
        game_data=game_data, user_id=callback.from_user.id
    )
    await callback.message.edit_reply_markup(reply_markup=markup)
    await game_state.set_data(game_data)


@router.callback_query(
    UserFsm.SUPERVISOR_COLLECTS_INFORMATION, F.data.isdigit()
)
async def supervisor_collects_information(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    game_state, game_data = await get_game_state_and_data(
        tg_obj=callback, state=state, dispatcher=dispatcher
    )
    checked = game_data[Warden.extra_data[0].key]
    processed_user_id = int(callback.data)
    if len(checked) == 1 and checked[0][0] == processed_user_id:
        checked.clear()
        await generate_markup_after_selection(
            callback=callback,
            game_state=game_state,
            game_data=game_data,
        )
        return
    elif len(checked) == 0:
        checked.append(
            [
                processed_user_id,
                game_data["players"][str(processed_user_id)][
                    "enum_name"
                ],
            ]
        )
        await generate_markup_after_selection(
            callback=callback,
            game_state=game_state,
            game_data=game_data,
        )
        return

    checked.append(
        [
            processed_user_id,
            game_data["players"][str(processed_user_id)][
                "enum_name"
            ],
        ]
    )
    user1_id = checked[0][0]
    user2_id = checked[1][0]
    for user_id in [user1_id, user2_id]:
        trace_all_actions(
            callback=callback, game_data=game_data, user_id=user_id
        )
        save_notification_message(
            game_data=game_data,
            processed_user_id=user_id,
            message=ROLE_IS_KNOWN,
            current_user_id=callback.from_user.id,
        )
    user1_url = game_data["players"][str(user1_id)]["url"]
    user2_url = game_data["players"][str(user2_id)]["url"]
    await delete_message(callback.message)
    await game_state.set_data(game_data)
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=Warden.message_to_group_after_action,
    )
    await callback.message.answer(
        NUMBER_OF_NIGHT.format(game_data["number_of_night"])
        + f"Ты решил проверить на принадлежность одной группировки {user1_url} и {user2_url}"
    )
