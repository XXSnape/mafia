from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from cache.cache_types import GameCache
from keyboards.inline.callback_factory.recognize_user import (
    AimedUserCbData,
    ProsAndCons,
)
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from services.roles import PrimeMinister, Prosecutor
from states.states import GameFsm
from utils.utils import add_voice

router = Router(name=__name__)


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
    if callback.from_user.id == Prosecutor().get_processed_user_id(
        game_data
    ):
        await callback.answer(
            "Ты арестован и не можешь голосовать!", show_alert=True
        )
        return
    if callback_data.action == ProsAndCons.pros:
        add_voice(
            user_id=callback.from_user.id,
            add_to=game_data["pros"],
            delete_from=game_data["cons"],
            prime_ministers=game_data.get(
                PrimeMinister.roles_key, []
            ),
        )
    elif callback_data.action == ProsAndCons.cons:
        add_voice(
            user_id=callback.from_user.id,
            add_to=game_data["cons"],
            delete_from=game_data["pros"],
            prime_ministers=game_data.get(
                PrimeMinister.roles_key, []
            ),
        )
    with suppress(TelegramBadRequest, AttributeError):
        await callback.message.edit_reply_markup(
            reply_markup=get_vote_for_aim_kb(
                user_id=callback_data.user_id,
                pros=game_data["pros"],
                cons=game_data["cons"],
            )
        )
    await callback.answer()
