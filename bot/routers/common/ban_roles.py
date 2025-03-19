from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, PollAnswer
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.repositories.prohibited_roles import (
    ProhibitedRolesDAO,
)

from keyboards.inline.cb.cb_text import (
    VIEW_BANNED_ROLES_CB,
    CANCEL_CB,
    COMPLETE_TO_BAN_CB,
    EDIT_BANNED_ROLES_CB,
    CLEAR_BANNED_ROLES_CB,
)
from keyboards.inline.keypads.settings import (
    select_setting_kb,
    go_to_following_roles_kb,
    edit_banned_roles_kb,
)
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from states.settings import SettingsFsm
from utils.roles import get_roles_without_bases

router = Router(name=__name__)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
router.message.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())
router.poll_answer.middleware(DatabaseMiddlewareWithCommit())


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


@router.callback_query(F.data == VIEW_BANNED_ROLES_CB)
async def view_banned_roles(
    callback: CallbackQuery, session_without_commit: AsyncSession
):
    dao = ProhibitedRolesDAO(session=session_without_commit)
    banned_roles = await dao.get_banned_roles(
        user_id=callback.from_user.id,
    )
    if banned_roles:
        message = "Забаненные роли:\n\n" + "\n".join(banned_roles)
    else:
        message = "Все роли могут участвовать в игре!"
    await callback.message.edit_text(
        text=message,
        reply_markup=edit_banned_roles_kb(
            are_there_roles=bool(message)
        ),
    )


@router.callback_query(F.data == CLEAR_BANNED_ROLES_CB)
async def clear_banned_roles(
    callback: CallbackQuery, session_with_commit: AsyncSession
):
    dao = ProhibitedRolesDAO(session=session_with_commit)
    await dao.save_new_prohibited_roles(
        user_id=callback.from_user.id,
        roles=None,
    )
    await callback.answer("Теперь для игры доступны все роли!")
    await callback.message.edit_text(
        "Выбери, что конкретно хочешь настроить",
        reply_markup=select_setting_kb(),
    )


@router.callback_query(F.data == EDIT_BANNED_ROLES_CB)
async def suggest_roles_to_ban(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(SettingsFsm.BAN_ROLES)
    current_number = 0
    available_roles, max_number = get_roles_without_bases(
        number=current_number
    )
    await callback.message.delete()
    poll = await callback.bot.send_poll(
        chat_id=callback.from_user.id,
        question="Какие роли хочешь забанить?",
        options=available_roles,
        allows_multiple_answers=True,
        is_anonymous=False,
        reply_markup=go_to_following_roles_kb(
            current_number=current_number,
            max_number=max_number,
            are_there_roles=False,
        ),
    )
    await state.set_data(
        {
            "number": current_number,
            "banned_roles": [],
            "poll_id": poll.message_id,
        },
    )


@router.poll_answer(SettingsFsm.BAN_ROLES)
async def process_banned_roles(
    poll_answer: PollAnswer,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    pool_data = await state.get_data()
    current_number = pool_data["number"]
    available_roles, max_number = get_roles_without_bases(
        number=current_number
    )
    banned_roles = pool_data["banned_roles"]
    ids = poll_answer.option_ids
    for role_id in ids:
        role_name = available_roles[role_id]
        if role_name not in banned_roles:
            banned_roles.append(role_name)
    await poll_answer.bot.delete_message(
        chat_id=poll_answer.user.id, message_id=pool_data["poll_id"]
    )
    await poll_answer.bot.send_message(
        chat_id=poll_answer.user.id,
        text="Забаненные роли:\n\n" + "\n".join(banned_roles),
    )
    if current_number + 1 > max_number:
        dao = ProhibitedRolesDAO(session=session_with_commit)
        await dao.save_new_prohibited_roles(
            user_id=poll_answer.user.id,
            roles=banned_roles,
        )
        return
    current_number += 1
    available_roles, max_number = get_roles_without_bases(
        number=current_number
    )
    poll = await poll_answer.bot.send_poll(
        chat_id=poll_answer.user.id,
        question="Какие роли хочешь забанить?",
        options=available_roles,
        allows_multiple_answers=True,
        reply_markup=go_to_following_roles_kb(
            current_number=current_number,
            max_number=max_number,
            are_there_roles=bool(banned_roles),
        ),
        is_anonymous=False,
    )
    await state.set_data(
        {
            "number": current_number,
            "banned_roles": banned_roles,
            "poll_id": poll.message_id,
        }
    )


@router.callback_query(SettingsFsm.BAN_ROLES, F.data.isdigit())
async def switch_pool(
    callback: CallbackQuery,
    state: FSMContext,
):
    poll_data = await state.get_data()
    banned_roles = poll_data["banned_roles"]
    current_number = int(callback.data)
    available_roles, max_number = get_roles_without_bases(
        number=current_number
    )
    await callback.message.delete()
    poll = await callback.bot.send_poll(
        chat_id=callback.from_user.id,
        question="Какие роли хочешь забанить?",
        options=available_roles,
        allows_multiple_answers=True,
        is_anonymous=False,
        reply_markup=go_to_following_roles_kb(
            current_number=current_number,
            max_number=max_number,
            are_there_roles=bool(banned_roles),
        ),
    )
    await state.update_data(
        {"number": current_number, "poll_id": poll.message_id}
    )


@router.callback_query(
    SettingsFsm.BAN_ROLES, F.data == COMPLETE_TO_BAN_CB
)
async def save_prohibited_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    pool_data = await state.get_data()
    banned_roles = pool_data["banned_roles"]
    dao = ProhibitedRolesDAO(session=session_with_commit)
    await dao.save_new_prohibited_roles(
        user_id=callback.from_user.id,
        roles=banned_roles,
    )
    await callback.answer(
        "✅Вы успешно забанили роли!", show_alert=True
    )
    await callback.message.delete()
    await callback.message.answer(
        text="✅Успешно забаненные роли:\n\n"
        + "\n".join(banned_roles),
    )
    await state.clear()
