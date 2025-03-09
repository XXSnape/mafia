from contextlib import suppress

from aiogram import Dispatcher, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatPermissions
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import (
    take_action_and_register_user,
)
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.PROSECUTOR_ARRESTS, UserActionIndexCbData.filter()
)
async def prosecutor_arrests(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    game_data, arrested_user_id = (
        await take_action_and_register_user(
            callback=callback,
            callback_data=callback_data,
            state=state,
            dispatcher=dispatcher,
            # message_to_group="По данным разведки потенциальный злоумышленник арестован!",
            # message_to_user="Ты выбрал арестовать {url}",
            # role=Roles.prosecutor,
            # last_processed_user_key="last_arrested",
            # list_to_process_key="cant_vote",
        )
    )
    # game_state, game_data, arrested_user_id = (
    #     await get_user_id_and_inform_players(
    #         callback=callback,
    #         callback_data=callback_data,
    #         state=state,
    #         dispatcher=dispatcher,
    #         message_to_group="По данным разведки потенциальный злоумышленник арестован!",
    #         message_to_user="Ты выбрал арестовать {url}",
    #     )
    # )
    with suppress(TelegramBadRequest):
        await callback.bot.restrict_chat_member(
            chat_id=game_data["game_chat"],
            user_id=arrested_user_id,
            permissions=ChatPermissions(can_send_messages=False),
        )
    # game_data["cant_vote"].append(arrested_user_id)
    # game_data["last_arrested"] = arrested_user_id
    # await game_state.set_data(game_data)

    # role = game_data["players"][str(checked_user_id)]["pretty_role"]
    # url = game_data["players"][str(checked_user_id)]["url"]
    # await callback.answer(f"{url} - {role}!", show_alert=True)
    # await callback.message.answer(f"{url} - {role}!")
    # user_data: UserCache = await state.get_data()
    # game_state = await get_state_and_assign(
    #     dispatcher=dispatcher,
    #     chat_id=user_data["game_chat"],
    #     bot_id=callback.bot.id,
    # )
    # game_data: GameCache = await game_state.get_data()
    # await callback.bot.send_message(
    #     chat_id=user_data["game_chat"],
    #     text="По данным разведки потенциальный злоумышленник арестован!",
    # )
    # arrested_user_id = game_data["players_ids"][
    #     callback_data.user_index
    # ]
    # with suppress(TelegramBadRequest):
    #     await callback.bot.restrict_chat_member(
    #         chat_id=game_data["game_chat"],
    #         user_id=arrested_user_id,
    #         permissions=ChatPermissions(can_send_messages=False),
    #     )
    # game_data["cant_vote"].append(arrested_user_id)
    # game_data["last_arrested"] = arrested_user_id
    # url = game_data["players"][str(arrested_user_id)]["url"]
    # await callback.message.delete()
    # await callback.message.answer(f"Ты выбрал арестовать {url}")
    # await game_state.set_data(game_data)
