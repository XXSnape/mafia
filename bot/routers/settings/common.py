from aiogram import F, Router
from aiogram.enums import ChatType
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

router = Router(name=__name__)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


@router.callback_query(F.data == MENU_CB)
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Доступные команды:\n\n/settings - настройки"
    )


@router.callback_query(F.data == CANCEL_CB)
async def cancel_state(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("/settings - настройки")


@router.message(Command("settings"), StateFilter(default_state))
async def handle_settings(
    message: Message,
):
    await message.delete()
    await message.answer(
        "Выбери, что конкретно хочешь настроить",
        reply_markup=select_setting_kb(),
    )


@router.callback_query(F.data == ACTIONS_FOR_ROLES_CB)
async def back_to_settings(
    callback: CallbackQuery, state: FSMContext
):
    await state.clear()
    await callback.message.edit_text(
        text="Выбери, что конкретно хочешь настроить",
        reply_markup=select_setting_kb(),
    )
