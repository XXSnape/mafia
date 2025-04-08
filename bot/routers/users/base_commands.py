from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.users import UsersDao
from database.schemas.common import TgId
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.callback_factory.help import RoleCbData
from keyboards.inline.cb.cb_text import VIEW_ROLES_CB, HELP_CB
from keyboards.inline.keypads.help import (
    help_options_kb,
    get_roles_kb,
    go_back_to_options_kb,
)
from utils.pretty_text import make_build

router = Router(name=__name__)


@router.message(CommandStart(), StateFilter(default_state))
async def greetings_to_user(
    message: Message, session_with_commit: AsyncSession
):
    await UsersDao(session=session_with_commit).get_user_or_create(
        tg_id=TgId(tg_id=message.from_user.id)
    )
    await message.answer(
        f"Привет, я бот ведущий в для мафии. Просто добавь меня в чат."
    )


@router.message(Command("help"))
async def handle_help_by_command(message: Message):
    await message.delete()
    text = (
        "Как играть?\n"
        "Просто добавь меня в чат и следуй инструкциям!"
    )
    await message.answer(
        make_build(text), reply_markup=help_options_kb()
    )


@router.callback_query(F.data == HELP_CB)
async def handle_help_by_callback(callback: CallbackQuery):
    await callback.message.delete()
    text = (
        "Как играть?\n"
        "Просто добавь меня в чат и следуй инструкциям!"
    )
    await callback.message.answer(
        make_build(text), reply_markup=help_options_kb()
    )


@router.callback_query(F.data == VIEW_ROLES_CB)
async def view_roles(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text="Выбери роль, чтобы узнать подробности о ней",
        reply_markup=get_roles_kb(),
    )


@router.callback_query(RoleCbData.filter())
async def get_details_about_role(
    callback: CallbackQuery, callback_data: RoleCbData
):
    current_role = get_data_with_roles(callback_data.role_id)
    await callback.message.delete()
    await callback.message.answer_photo(
        photo=current_role.photo,
        caption=f"Название {current_role.role}",
        reply_markup=go_back_to_options_kb(),
    )
