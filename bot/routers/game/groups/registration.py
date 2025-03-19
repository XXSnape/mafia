from aiogram import Dispatcher, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.cache_types import GameCache
from keyboards.inline.cb.cb_text import FINISH_REGISTRATION_CB, JOIN_CB
from keyboards.inline.keypads.join import get_join_kb
from services.pipeline_game import Game
from services.registartion import add_user_to_game, init_game
from states.states import GameFsm
from utils.utils import get_profiles_during_registration

router = Router(name=__name__)


@router.message(Command("registration"), StateFilter(default_state))
async def start_registration(
    message: Message,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
    dispatcher: Dispatcher,
):
    await message.delete()
    await init_game(state=state, message=message)
    live_players, players = await add_user_to_game(
        dispatcher=dispatcher, tg_obj=message, state=state
    )
    sent_message = await message.answer(
        get_profiles_during_registration(live_players, players),
        reply_markup=get_join_kb(),
    )
    await sent_message.pin()
    # scheduler.add_job(
    #     start_game_by_timer,
    #     "date",
    #     run_date=datetime.now() + timedelta(seconds=5),
    #     kwargs={
    #         "chat_id": message.chat.id,
    #         "message_id": sent_message.message_id,
    #         "bot": message.bot,
    #         "state": state,
    #     },
    # )


@router.callback_query(GameFsm.REGISTRATION, F.data == JOIN_CB)
async def join_new_member(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    game_cache: GameCache = await state.get_data()
    ids: list[int] = game_cache["players_ids"]
    if callback.from_user.id in ids:
        await callback.answer(
            "Ты уже успешно зарегистрировался!", show_alert=True
        )
        return
    live_players, players = await add_user_to_game(
        dispatcher=dispatcher, tg_obj=callback, state=state
    )
    await callback.answer("Ты в игре! Удачи!", show_alert=True)
    await callback.message.edit_text(
        text=get_profiles_during_registration(live_players, players),
        reply_markup=get_join_kb(),
    )


@router.callback_query(
    GameFsm.REGISTRATION, F.data == FINISH_REGISTRATION_CB
)
async def finish_registration(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
    scheduler: AsyncIOScheduler,
):
    game_data: GameCache = await state.get_data()
    if game_data["owner"] != callback.from_user.id:
        await callback.answer(
            "Пожалуйста, попросите создателя начать игру",
            show_alert=True,
        )
        return
    if len(game_data["players_ids"]) < 3:
        await callback.answer(
            "Слишком мало игроков", show_alert=True
        )
        return
    game = Game(
        message=callback.message,
        state=state,
        dispatcher=dispatcher,
        scheduler=scheduler,
    )
    await game.start_game()
