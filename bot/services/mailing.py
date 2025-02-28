from aiogram import Bot
from aiogram.fsm.context import FSMContext

from cache.cache_types import GameCache


async def familiarize_players(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    mafias = game_data["mafias"]

    for user_id in mafias:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - мафия! Тебе нужно уничтожить всех горожан.",
        )
