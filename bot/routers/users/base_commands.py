from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import Grouping
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.users import UsersDao
from database.schemas.common import TgId
from general.collection_of_roles import get_data_with_roles
from general.groupings import Groupings
from keyboards.inline.callback_factory.help import RoleCbData
from keyboards.inline.cb.cb_text import VIEW_ROLES_CB, HELP_CB
from keyboards.inline.keypads.help import (
    help_options_kb,
    get_roles_kb,
    go_back_to_options_kb,
)
from utils.pretty_text import make_build, make_pretty

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
        "Просто добавь меня в чат и следуй инструкциям!\n"
        "Базовая информация о ролях:"
        "- В случае поражения "
    )
    await callback.message.answer(
        make_build(text), reply_markup=help_options_kb()
    )


@router.callback_query(F.data == VIEW_ROLES_CB)
async def view_roles(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text=(
            make_build(
                "Базовая информация о ролях:\n"
                "● В случае поражения деньги ни за что не начисляются\n"
                "● Ночные роли в основном не могут выбирать себя\n"
                "● У роли могут быть союзники, которые вступят в основную должность после смерти главаря"
            )
        ),
        reply_markup=get_roles_kb(),
    )


def join(strings: list[str] | None):
    if strings is None:
        return "Нет"
    strings = [string.capitalize() for string in strings]
    return "\n● " + "\n● ".join(strings)


@router.callback_query(RoleCbData.filter())
async def get_details_about_role(
    callback: CallbackQuery, callback_data: RoleCbData
):
    current_role = get_data_with_roles(callback_data.role_id)
    description = current_role.role_description
    if current_role.is_alias:
        text = (
            f"Роль является союзной к {make_pretty(current_role.boss_name)}. "
            f"В случае смерти главаря вступает в должность рандомный союзник\n\n"
        )
        if current_role.is_mass_mailing_list:
            text += "Может влиять на выбор ночью"
        else:
            text += "Не может влиять на выбор ночью"
    else:
        text = (
            f"🏆Условие победы: {description.wins_if.capitalize()}\n\n"
            f"💪Особый навык: {(description.skill or "Нет").capitalize()}\n\n"
            f"💰Платят за: {join(description.pay_for)}\n\n"
            f"🚫Ограничения: {join(description.limitations)}\n\n"
            f"✨Особенности: {join(description.features)}"
        )

    common_text = (
        f"🪪Название: {make_pretty(current_role.role)}\n\n"
        f"🎭Группировка: {make_build(current_role.grouping.value.name)}\n\n"
    )
    purpose_of_grouping = None
    if current_role.grouping in (
        Groupings.criminals,
        Groupings.killer,
    ):
        purpose_of_grouping = (
            f"Сделать так, чтобы "
            f"представителей группы стало больше "
            f"или равно остальным остальным участникам игры"
        )
    elif current_role.grouping == Groupings.civilians:
        purpose_of_grouping = (
            f"Уничтожить группировки {Groupings.criminals.value.name} "
            f"и {Groupings.killer.value.name}"
        )
    if purpose_of_grouping:
        common_text += (
            f"🎯Цель группировки: {purpose_of_grouping}\n\n"
        )

    result_text = common_text + text

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=current_role.photo,
        caption=make_build(result_text),
        reply_markup=go_back_to_options_kb(),
    )
