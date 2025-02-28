from aiogram import Router, F, Dispatcher
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from cache.cache_types import GameCache, UserGameCache
from keyboards.inline.cb.cb_text import JOIN_CB, FINISH_REGISTRATION_CB
from keyboards.inline.keypads.join import get_join_kb
from states.states import GameFsm, UserFsm
from tasks.tasks import start_first_night

router = Router()

router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))


@router.message(Command("registration"), StateFilter(default_state))
async def start_registration(
    message: Message,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
    dispatcher: Dispatcher,
):

    state_with: FSMContext = FSMContext(
        # bot=bot,  # объект бота
        storage=dispatcher.storage,  # dp - экземпляр диспатчера
        key=StorageKey(
            chat_id=message.from_user.id,  # если юзер в ЛС, то chat_id=user_id
            user_id=message.from_user.id,
            bot_id=message.bot.id,
        ),
    )
    await state_with.update_data(
        {"game": message.chat.id}
    )  # обновить дату для пользователя
    await state_with.set_state(UserFsm.ACTION)  # пример присвоения стейта

    await state.set_state(GameFsm.REGISTRATION)
    user_data: UserGameCache = {"fullname": message.from_user.full_name}
    game_cache: GameCache = {
        "owner": message.from_user.id,
        "players_ids": [message.from_user.id],
        "players": {str(message.from_user.id): user_data},
    }
    await state.update_data(game_cache)
    url = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>'
    sent_message = await message.answer(
        f"Скорее присоединяйся к игре!\nУчастники:\n- {url}",
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
async def join_new_member(callback: CallbackQuery, state: FSMContext):
    ids: list[int] = (await state.get_data())[PLAYERS_IDS_KEY]
    if callback.from_user.id in ids:
        await callback.answer(
            "Ты уже успешно зарегистрировался!", show_alert=True
        )
        return
    ids.append(callback.from_user.id)
    await callback.answer("Ты в игре! Удачи!", show_alert=True)
    print("text", callback.message.text)
    await callback.message.edit_text(
        text=callback.message.text + f"\n- {callback.from_user.full_name}",
        reply_markup=get_join_kb(),
    )


# -1002327574177
@router.message(Command("s"), UserFsm.ACTION)
async def h(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    await message.answer("hello!")
    user_data = await state.get_data()
    print(f"{user_data=}")
    s = FSMContext(
        # bot=bot,  # объект бота
        storage=dispatcher.storage,  # dp - экземпляр диспатчера
        key=StorageKey(
            chat_id=user_data["game"],  # если юзер в ЛС, то chat_id=user_id
            user_id=user_data["game"],
            bot_id=message.bot.id,
        ),
    )
    print("game data", await s.get_data())


@router.message(GameFsm.REGISTRATION, F.data == FINISH_REGISTRATION_CB)
async def finish_registration(callback: CallbackQuery, state: FSMContext):
    owner = (await state.get_data())[OWNER_GAME_KEY]
    if owner != callback.from_user.id:
        await callback.answer(
            "Пожалуйста, попросите создателя начать игру", show_alert=True
        )
        return
    await start_first_night(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        bot=callback.bot,
        state=state,
    )
