from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
    UserVoteIndexCbData,
)
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from services.game.actions_at_night import (
    get_game_state_data_and_user_id,
)
from services.game.roles import Instigator
from utils.tg import delete_message

router = Router(name=__name__)


@router.callback_query(UserVoteIndexCbData.filter())
async def vote_for(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    game_state, game_data, voted_user_id = (
        await get_game_state_data_and_user_id(
            callback=callback,
            callback_data=callback_data,
            state=state,
            dispatcher=dispatcher,
        )
    )
    deceived_user = game_data.get(Instigator.extra_data[0].key)
    if (
        deceived_user
        and callback.from_user.id == deceived_user[0][0]
    ):
        voted_user_id = deceived_user[0][1]
    game_data["vote_for"].append(
        [callback.from_user.id, voted_user_id]
    )
    voting_url = game_data["players"][str(callback.from_user.id)][
        "url"
    ]
    voted_url = game_data["players"][str(voted_user_id)]["url"]
    await delete_message(callback.message)
    await callback.message.answer(
        f"Ты выбрал голосовать за {voted_url}"
    )
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=f"{voting_url} выступает против {voted_url}!",
        reply_markup=participate_in_social_life(),
    )
