from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import UserCache, GameCache
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from utils.utils import get_state_and_assign


# async def f(
#     callback,
#     callback_data,
#     state,
#     dispatcher,
# ):
#     user_data: UserCache = await state.get_data()
#     game_state = await get_state_and_assign(
#         dispatcher=dispatcher,
#         chat_id=user_data["game_chat"],
#         bot_id=callback.bot.id,
#     )
#     game_data: GameCache = await game_state.get_data()
#     await callback.bot.send_message(
#         chat_id=user_data["game_chat"],
#         text="РАБОТАЕТ местная полиция!",
#     )
#     checked_user_id = game_data["players_ids"][
#         callback_data.user_index
#     ]
#     # await callback.bot.send_message(
#     #     chat_id=checked_user_id,
#     #     text="Тебе же нечего скрывать, да? Оперативные службы проводят в отношении тебя тщательную проверку",
#     # )
#     role = game_data["players"][str(checked_user_id)]["pretty_role"]
#     url = game_data["players"][str(checked_user_id)]["url"]
#     await callback.message.delete()
#     await callback.message.answer(f"{url} - {role}!")


async def get_user_id_and_inform_players(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
    message_to_group: str,
    message_to_user: str,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    await callback.bot.send_message(
        chat_id=user_data["game_chat"],
        text=message_to_group,
    )
    user_id = game_data["players_ids"][callback_data.user_index]
    url = game_data["players"][str(user_id)]["url"]
    await callback.message.delete()
    await callback.message.answer(message_to_user.format(url=url))
    return game_state, game_data, user_id
