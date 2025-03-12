from random import choice

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from cache.cache_types import GameCache, UserCache
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
    UserVoteIndexCbData,
)
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from services.roles import Instigator
from utils.utils import get_state_and_assign

router = Router(name=__name__)


@router.callback_query(UserVoteIndexCbData.filter())
async def vote_for(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    voted_user_id = game_data["players_ids"][
        callback_data.user_index
    ]
    if callback.from_user.id == Instigator().get_processed_user_id(
        game_data
    ):
        ids = game_data["players_ids"][:]
        ids.remove(callback.from_user.id)
        ids.remove(voted_user_id)
        voted_user_id = choice(ids)
    game_data["vote_for"].append(
        [callback.from_user.id, voted_user_id]
    )
    voting_url = game_data["players"][str(callback.from_user.id)][
        "url"
    ]
    voted_url = game_data["players"][str(voted_user_id)]["url"]
    await callback.message.delete()
    await callback.message.answer(
        f"Ты выбрал голосовать за {voted_url}"
    )
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=f"{voting_url} выступает против {voted_url}!",
        reply_markup=participate_in_social_life(),
    )
