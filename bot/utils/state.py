import asyncio
from contextlib import asynccontextmanager, suppress
from typing import cast

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from cache.cache_types import GameCache, UserCache, UserIdInt
from utils.tg import delete_messages_from_to_delete


async def get_state_and_assign(
    dispatcher: Dispatcher,
    chat_id: int,
    bot_id: int,
    new_state: State | None = None,
) -> FSMContext:
    chat_state: FSMContext = FSMContext(
        storage=dispatcher.storage,
        key=StorageKey(
            chat_id=chat_id,
            user_id=chat_id,
            bot_id=bot_id,
        ),
    )
    if new_state:
        await chat_state.set_state(new_state)
    return chat_state


@asynccontextmanager
async def lock_state(state: FSMContext):
    storage = cast(RedisStorage, state.storage)
    isolation = storage.create_isolation()
    async with isolation.lock(state.key):
        yield None


async def reset_user_state(
    dispatcher: Dispatcher, user_id: int, bot_id: int
):
    state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_id,
        bot_id=bot_id,
    )
    await state.clear()


async def reset_user_state_if_in_game(
    dispatcher: Dispatcher, user_id: int, bot_id: int, group_id: int
):
    state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_id,
        bot_id=bot_id,
    )
    user_game_data: UserCache = await state.get_data()
    if user_game_data.get("game_chat") != group_id:
        return
    await state.clear()


async def reset_state_to_all_users(
    dispatcher: Dispatcher, bot_id: int, users_ids: list[UserIdInt]
):
    await asyncio.gather(
        *(
            [
                reset_user_state(
                    dispatcher=dispatcher,
                    user_id=user_id,
                    bot_id=bot_id,
                )
                for user_id in users_ids
            ]
        )
    )


async def clear_game_data(
    game_data: GameCache,
    bot: Bot,
    dispatcher: Dispatcher,
    state: FSMContext,
    message_id: int,
):
    with suppress(TelegramBadRequest):
        await bot.delete_message(
            chat_id=game_data["game_chat"], message_id=message_id
        )
    await delete_messages_from_to_delete(
        bot=bot,
        state=state,
    )
    await reset_state_to_all_users(
        dispatcher=dispatcher,
        bot_id=bot.id,
        users_ids=game_data["live_players_ids"],
    )
    await state.clear()
