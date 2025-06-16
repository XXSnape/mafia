from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from general.commands import PrivateCommands
from keyboards.inline.callback_factory.shop import (
    BuyResourcesCbData,
    ChooseToPurchaseCbData,
)
from keyboards.inline.cb.cb_text import (
    SHOP_CB,
)
from services.users.shop import ShopManager
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)


@router.message(Command(PrivateCommands.shop.name))
async def show_assets_by_message(
    message: Message,
    session_without_commit: AsyncSession,
):
    shop_manager = ShopManager(
        message=message, session=session_without_commit
    )
    await shop_manager.show_assets(user_tg_id=message.from_user.id)


@router.callback_query(F.data == SHOP_CB)
async def show_assets_by_callback(
    callback: CallbackQuery,
    session_without_commit: AsyncSession,
):
    shop_manager = ShopManager(
        message=callback.message, session=session_without_commit
    )
    await shop_manager.show_assets(user_tg_id=callback.from_user.id)


@router.callback_query(ChooseToPurchaseCbData.filter())
async def select_number_of_resources(
    callback: CallbackQuery,
    callback_data: ChooseToPurchaseCbData,
    session_without_commit: AsyncSession,
):
    shop_manager = ShopManager(
        callback=callback, session=session_without_commit
    )
    await shop_manager.select_number_of_resources(
        callback_data=callback_data
    )


@router.callback_query(
    BuyResourcesCbData.filter(F.is_confirmed.is_(False))
)
async def confirm_purchase_of_resource(
    callback: CallbackQuery,
    callback_data: BuyResourcesCbData,
    session_without_commit: AsyncSession,
):
    shop_manager = ShopManager(
        callback=callback, session=session_without_commit
    )
    await shop_manager.confirm_purchase_of_resource(
        callback_data=callback_data
    )


@router.callback_query(
    BuyResourcesCbData.filter(F.is_confirmed.is_(True))
)
async def buy_resources(
    callback: CallbackQuery,
    callback_data: BuyResourcesCbData,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    shop_manager = ShopManager(
        callback=callback, session=session_with_commit, state=state
    )
    await shop_manager.buy_resources(callback_data=callback_data)
