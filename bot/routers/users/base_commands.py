from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import Grouping
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.users import UsersDao
from database.schemas.common import TgId
from general import settings
from general.collection_of_roles import get_data_with_roles
from general.commands import BotCommands
from general.groupings import Groupings
from general.text import ROLES_SELECTION, CONFIGURE_GAME_SECTION
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import HELP_BTN
from keyboards.inline.callback_factory.help import RoleCbData
from keyboards.inline.cb.cb_text import (
    VIEW_ROLES_CB,
    HELP_CB,
    HOW_TO_START_GAME_CB,
    WHAT_ARE_BIDS_CB,
    HOW_TO_PLAY_CB,
    HOW_TO_SET_UP_GAME_CB,
    HOW_TO_SEE_STATISTICS_CB,
)
from keyboards.inline.keypads.help import (
    help_options_kb,
    get_roles_kb,
    go_back_to_options_kb,
    to_help_kb,
    ROLES_SELECTION_BTN,
    HOW_TO_SET_UP_GAME_BTN,
)
from mafia.roles import Instigator, Warden
from services.users.base import BaseRouter
from utils.pretty_text import make_build, make_pretty

router = Router(name=__name__)


@router.message(CommandStart(), StateFilter(default_state))
async def greetings_to_user(
    message: Message, session_with_commit: AsyncSession
):
    base = BaseRouter(
        message=message,
        session=session_with_commit,
    )
    await base.greetings_to_user()


@router.message(Command("help"))
async def handle_help_by_command(message: Message):
    base = BaseRouter(message=message)
    await base.handle_help()


@router.callback_query(F.data == HELP_CB)
async def handle_help_by_callback(callback: CallbackQuery):
    base = BaseRouter(message=callback.message)
    await base.handle_help()


@router.callback_query(F.data == VIEW_ROLES_CB)
async def view_roles(callback: CallbackQuery):
    base = BaseRouter(callback=callback)
    await base.view_roles()


@router.callback_query(F.data == HOW_TO_START_GAME_CB)
async def how_to_start_game(callback: CallbackQuery):
    base = BaseRouter(callback=callback)
    await base.how_to_start_game()


@router.callback_query(F.data == WHAT_ARE_BIDS_CB)
async def what_are_bids(callback: CallbackQuery):
    base = BaseRouter(callback=callback)
    await base.what_are_bids()


@router.callback_query(F.data == HOW_TO_PLAY_CB)
async def how_to_play(callback: CallbackQuery):
    base = BaseRouter(callback=callback)
    await base.how_to_play()


@router.callback_query(F.data == HOW_TO_SET_UP_GAME_CB)
async def how_to_set_up_game(callback: CallbackQuery):
    base = BaseRouter(callback=callback)
    await base.how_to_set_up_game()


@router.callback_query(F.data == HOW_TO_SEE_STATISTICS_CB)
async def how_to_see_statistics(callback: CallbackQuery):
    base = BaseRouter(callback=callback)
    await base.how_to_see_statistics()


@router.callback_query(RoleCbData.filter())
async def get_details_about_role(
    callback: CallbackQuery, callback_data: RoleCbData
):
    base = BaseRouter(callback=callback)
    await base.get_details_about_role(callback_data=callback_data)
