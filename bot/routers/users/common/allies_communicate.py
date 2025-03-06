import asyncio

from aiogram import F, Dispatcher, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from cache.cache_types import UserCache, GameCache

from states.states import UserFsm
from utils.utils import get_state_and_assign


router = Router(name=__name__)


@router.message(
    StateFilter(
        UserFsm.DON_ATTACKS,
        UserFsm.MAFIA_ATTACKS,
        UserFsm.POLICEMAN_CHECKS,
        UserFsm.DOCTOR_TREATS,
    ),
    F.text,
)
async def allies_communicate(
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
    url = game_data["players"][str(message.from_user.id)]["url"]
    role = game_data["players"][str(message.from_user.id)][
        "pretty_role"
    ]
    aliases = game_data["players"][str(message.from_user.id)][
        "roles_key"
    ]
    await asyncio.gather(
        *(
            message.bot.send_message(
                chat_id=player_id,
                text=f"{role} {url} передает:\n\n{message.text}",
            )
            for player_id in game_data[aliases]
            if player_id != message.from_user.id
        )
    )
    if message.from_user.id in game_data["mafias"] and game_data.get(
        "hackers"
    ):
        for hacker_id in game_data["hackers"]:
            await message.bot.send_message(
                chat_id=hacker_id,
                text=f"{role} ??? передает:\n\n{message.text}",
            )
    if len(game_data[aliases]) > 1:
        await message.answer("Сообщение успешно отправлено!")
