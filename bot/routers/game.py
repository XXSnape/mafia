from contextlib import suppress
from datetime import timedelta

from aiogram import Router, F, Dispatcher, Bot
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, ChatPermissions
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from cache.cache_types import GameCache
from keyboards.inline.callback_factory.recognize_user import (
    AimedUserCbData,
    ProsAndCons,
)
from keyboards.inline.cb.cb_text import (
    JOIN_CB,
    FINISH_REGISTRATION_CB,
)
from keyboards.inline.keypads.join import get_join_kb
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from services.mailing import familiarize_players
from services.registartion import (
    add_user_to_game,
    init_game,
    select_roles,
)
from states.states import GameFsm, UserFsm
from tasks.tasks import start_game, start_night
from utils.utils import (
    get_profiles,
    get_profiles_during_registration,
    add_voice,
)

router = Router()

router.message.filter(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
router.callback_query.filter(
    F.message.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)


@router.message(GameFsm.STARTED)
async def delete_message_from_non_players(
    message: Message, state: FSMContext
):
    game_data: GameCache = await state.get_data()
    if message.from_user.id not in game_data["players_ids"]:
        await message.delete()
        # await message.chat.restrict(
        #     user_id=message.from_user.id,
        #     permissions=ChatPermissions(can_send_messages=False),
        #     until_date=timedelta(seconds=30),
        # )


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
    bot: Bot,
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
    await select_roles(state=state)
    await familiarize_players(bot=callback.bot, state=state)
    await start_game(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        bot=callback.bot,
        state=state,
        dispatcher=dispatcher,
        scheduler=scheduler,
    )


@router.callback_query(GameFsm.VOTE, AimedUserCbData.filter())
async def confirm_vote(
    callback: CallbackQuery,
    callback_data: AimedUserCbData,
    state: FSMContext,
):
    if callback_data.user_id == callback.from_user.id:
        await callback.answer(
            "Теперь твой судья - демократия!", show_alert=True
        )
        return
    game_data: GameCache = await state.get_data()
    if callback_data.action == ProsAndCons.pros:
        add_voice(
            user_id=callback.from_user.id,
            add_to=game_data["pros"],
            delete_from=game_data["cons"],
        )
    elif callback_data.action == ProsAndCons.cons:
        add_voice(
            user_id=callback.from_user.id,
            add_to=game_data["cons"],
            delete_from=game_data["pros"],
        )
    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(
            reply_markup=get_vote_for_aim_kb(
                user_id=callback_data.user_id,
                pros=game_data["pros"],
                cons=game_data["cons"],
            )
        )
    await callback.answer()
