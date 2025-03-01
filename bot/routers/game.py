from aiogram import Router, F, Dispatcher, Bot
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from cache.cache_types import GameCache
from keyboards.inline.cb.cb_text import (
    JOIN_CB,
    FINISH_REGISTRATION_CB,
)
from keyboards.inline.keypads.join import get_join_kb
from services.mailing import familiarize_players
from services.registartion import (
    add_user_to_game,
    init_game,
)
from states.states import GameFsm, UserFsm
from tasks.tasks import start_game, start_night
from utils.utils import (
    get_profiles,
    get_profiles_during_registration,
)

router = Router()

router.message.filter(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
router.callback_query.filter(
    F.message.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)


@router.message(Command("registration"), StateFilter(default_state))
async def start_registration(
    message: Message,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
    dispatcher: Dispatcher,
):
    await message.delete()
    await init_game(state=state, message=message)
    profiles = await add_user_to_game(
        dispatcher=dispatcher, tg_obj=message, state=state
    )
    sent_message = await message.answer(
        get_profiles_during_registration(profiles),
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
    profiles = await add_user_to_game(
        dispatcher=dispatcher, tg_obj=callback, state=state
    )
    await callback.answer("Ты в игре! Удачи!", show_alert=True)
    await callback.message.edit_text(
        text=get_profiles_during_registration(profiles),
        reply_markup=get_join_kb(),
    )


@router.callback_query(
    GameFsm.REGISTRATION, F.data == FINISH_REGISTRATION_CB
)
async def finish_registration(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    dispatcher: Dispatcher,
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
    await start_game(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        bot=callback.bot,
        state=state,
    )
    await familiarize_players(bot=callback.bot, state=state)
    await start_night(
        bot=bot,
        dispatcher=dispatcher,
        state=state,
        chat_id=callback.message.chat.id,
    )
