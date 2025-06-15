from aiogram import F, Router
from aiogram.types import CallbackQuery
from database.dao.users import UsersDao
from database.schemas.common import TgIdSchema
from general.text import MONEY_SYM
from keyboards.inline.callback_factory.shop import (
    ChooseToPurchaseCbData,
)

from keyboards.inline.cb.cb_text import (
    SHOP_CB,
)
from keyboards.inline.keypads.shop import available_resources_kb
from sqlalchemy.ext.asyncio import AsyncSession
from utils.pretty_text import make_build

router = Router(name=__name__)


@router.callback_query(F.data == SHOP_CB)
async def show_assets(
    callback: CallbackQuery,
    session_without_commit: AsyncSession,
):
    user = await UsersDao(
        session=session_without_commit
    ).get_user_or_create(TgIdSchema(tg_id=callback.from_user.id))
    resource_text = (
        f"💰Баланс: {user.balance}{MONEY_SYM}\n\n"
        f"💌Анонимки: {user.anonymous_letters}\n\n"
        f"🛒🛍️Выбери, что хочешь купить"
    )
    markup = available_resources_kb()
    await callback.message.edit_text(
        text=make_build(resource_text), reply_markup=markup
    )


@router.callback_query(ChooseToPurchaseCbData.filter())
async def select_number_of_resources(
    callback: CallbackQuery,
    session_without_commit: AsyncSession,
):

    pass
