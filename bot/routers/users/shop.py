from typing import assert_never

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton

from database.dao.assets import AssetsDao
from database.dao.users import UsersDao
from database.schemas.assets import AssetsSchema
from database.schemas.common import TgIdSchema
from general.resources import (
    Resources,
    get_data_about_resource,
    get_cost_of_discounted_resource,
)
from general.text import MONEY_SYM
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import SHOP_BTN
from keyboards.inline.callback_factory.shop import (
    ChooseToPurchaseCbData,
    BuyResourcesCbData,
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
        f"🛍️Доступные ресурсы:\n\n"
        f"💌Анонимки: {user.anonymous_letters}\n\n"
        f"🛒️Выбери, что хочешь докупить"
    )
    markup = available_resources_kb()
    await callback.message.edit_text(
        text=make_build(resource_text), reply_markup=markup
    )


@router.callback_query(ChooseToPurchaseCbData.filter())
async def select_number_of_resources(
    callback: CallbackQuery,
    callback_data: ChooseToPurchaseCbData,
    session_without_commit: AsyncSession,
):
    resource = callback_data.resource
    user = await UsersDao(
        session=session_without_commit
    ).get_user_or_create(TgIdSchema(tg_id=callback.from_user.id))
    resource_count = getattr(user, resource.value)

    asset = await AssetsDao(
        session=session_without_commit
    ).find_one_or_none(AssetsSchema(name=resource))
    asset_data = get_data_about_resource(resource=resource)
    text = asset_data.description

    prices = ""
    buttons = []
    for count in [1, 3, 5, 10, 15, 20]:
        cost = get_cost_of_discounted_resource(
            cost=asset.cost, count=count
        )
        buttons.append(
            InlineKeyboardButton(
                text=f"{count} ({cost}{MONEY_SYM})",
                callback_data=BuyResourcesCbData(
                    resource=resource,
                    count=count,
                    is_confirmed=False,
                ).pack(),
            )
        )
        prices += f"\n{count} шт: {cost}{MONEY_SYM}"
    buttons.append(SHOP_BTN)
    text += (
        f"💰Баланс: {user.balance}{MONEY_SYM}\n"
        f"🧰Текущее количество: {resource_count}\n\n"
        f"📈Цены:\n{prices}"
    )
    markup = generate_inline_kb(
        data_with_buttons=buttons, sizes=(2,)
    )
    await callback.message.edit_text(
        text=make_build(text), reply_markup=markup
    )


@router.callback_query(
    BuyResourcesCbData.filter(F.is_confirmed.is_(False))
)
async def confirm_purchase_of_resource(
    callback: CallbackQuery,
    callback_data: BuyResourcesCbData,
    session_without_commit: AsyncSession,
):
    asset_data = get_data_about_resource(
        resource=callback_data.resource
    )
    asset = await AssetsDao(
        session=session_without_commit
    ).find_one_or_none(AssetsSchema(name=callback_data.resource))
    cost = get_cost_of_discounted_resource(
        cost=asset.cost, count=callback_data.count
    )
    message = (
        f"❗️Ты уверен, что хочешь купить «{asset_data.name}» "
        f"в количестве {callback_data.count} шт за {cost}{MONEY_SYM}?"
    )
    callback_data.is_confirmed = True
    await callback.message.edit_text(
        text=make_build(message),
        reply_markup=generate_inline_kb(
            data_with_buttons=(
                InlineKeyboardButton(
                    text="🎁Купить",
                    callback_data=callback_data.pack(),
                ),
                InlineKeyboardButton(
                    text="❌Отмена", callback_data=SHOP_CB
                ),
            )
        ),
    )
