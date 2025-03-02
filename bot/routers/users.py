from aiogram import Router, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from cache.cache_types import UserCache, GameCache
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
    UserVoteIndexCbData,
)
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from utils.utils import get_state_and_assign
from states.states import UserFsm

router = Router()


@router.callback_query(
    UserFsm.MAFIA_ATTACKS, UserActionIndexCbData.filter()
)
async def mafia_attacks(
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
    await callback.bot.send_message(
        chat_id=user_data["game_chat"], text="Мафия выбрала жертву!"
    )
    died_user_id = game_data["players_ids"][callback_data.user_index]
    # await callback.bot.send_message(
    #     chat_id=died_user_id,
    #     text="Мафия уже рядом, тебе поможет только чудо",
    # )
    game_data["died"].append(died_user_id)
    url = game_data["players"][str(died_user_id)]["url"]
    await callback.message.delete()
    await callback.message.answer(f"Ты выбрал убить {url}")


@router.callback_query(
    UserFsm.DOCTOR_TREATS, UserActionIndexCbData.filter()
)
async def doctor_treats(
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
    await callback.bot.send_message(
        chat_id=user_data["game_chat"],
        text="Доктор спешит кому-то на помощь!",
    )

    recovered_user_id = game_data["players_ids"][
        callback_data.user_index
    ]
    # await callback.bot.send_message(
    #     chat_id=recovered_user_id,
    #     text="Врачи не забыли клятву Гиппократа и делают все возможное для твоего спасения!",
    # )
    game_data["recovered"].append(recovered_user_id)
    url = game_data["players"][str(recovered_user_id)]["url"]
    game_data["last_treated"] = recovered_user_id
    await callback.message.delete()
    await callback.message.answer(f"Ты выбрал вылечить {url}")
    await game_state.set_data(game_data)


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS, UserActionIndexCbData.filter()
)
async def policeman_checks(
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
    await callback.bot.send_message(
        chat_id=user_data["game_chat"],
        text="РАБОТАЕТ местная полиция!",
    )
    checked_user_id = game_data["players_ids"][
        callback_data.user_index
    ]
    # await callback.bot.send_message(
    #     chat_id=checked_user_id,
    #     text="Тебе же нечего скрывать, да? Оперативные службы проводят в отношении тебя тщательную проверку",
    # )
    role = game_data["players"][str(checked_user_id)]["pretty_role"]
    url = game_data["players"][str(checked_user_id)]["url"]
    await callback.message.delete()
    await callback.message.answer(f"{url} - {role}!")


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
    game_data["vote_for"].append(voted_user_id)
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


@router.message(F.text, UserFsm.WAIT_FOR_LATEST_LETTER)
async def send_latest_message(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=message.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    role = game_data["players"][str(message.from_user.id)]["role"]
    url = game_data["players"][str(message.from_user.id)]["url"]
    await message.bot.send_message(
        chat_id=user_data["game_chat"],
        text=f"По слухам {role} {url} перед смертью проглаголил такие слова:\n\n{message.text}",
    )
    await message.answer("Сообщение успешно отправлено!")
    await state.set_state(state=None)
