from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from keyboards.inline.cb.cb_text import (
    CANCEL_CB,
    MENU_CB,
    ACTIONS_FOR_ROLES_CB,
)
from keyboards.inline.keypads.settings import select_setting_kb
from states.settings import SettingsFsm
from utils.pretty_text import make_build

router = Router(name=__name__)


@router.message(
    Command("my_settings"),
    StateFilter(
        default_state,
        SettingsFsm.BAN_ROLES,
        SettingsFsm.ORDER_OF_ROLES,
    ),
)
async def handle_settings(message: Message, state: FSMContext):
    await state.clear()
    await message.delete()
    await message.answer(
        make_build("⚙️Выбери, что конкретно хочешь настроить"),
        reply_markup=select_setting_kb(),
    )


@router.callback_query(F.data == ACTIONS_FOR_ROLES_CB)
async def back_to_settings(
    callback: CallbackQuery, state: FSMContext
):
    await state.clear()
    await callback.message.edit_text(
        text=make_build("Выбери, что конкретно хочешь настроить"),
        reply_markup=select_setting_kb(),
    )
