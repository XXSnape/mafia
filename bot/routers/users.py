from aiogram import Router, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import PollAnswer

from cache.cache_types import UserCache, GameCache
from services.registartion import get_state_and_assign
from states.states import UserFsm

router = Router()


@router.poll_answer(UserFsm.MAFIA_ATTACK)
async def poll_answer_handler(
    poll_answer: PollAnswer,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=poll_answer.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    print(f"{game_data=}")
    await poll_answer.bot.stop_poll(
        chat_id=poll_answer.user.id,
        message_id=game_data["mafia_poll_delete"],
    )
    print(poll_answer.option_ids)
    options = [
        player_id
        for player_id in game_data["players_ids"]
        if player_id != poll_answer.user.id
    ]
    game_data["died"].append(options[poll_answer.option_ids[0]])
    await poll_answer.bot.send_message(
        chat_id=poll_answer.user.id, text="Ты сделал свой выбор!"
    )
