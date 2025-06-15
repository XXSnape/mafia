from services.base import RouterHelper

from aiogram.types import InlineKeyboardButton

from database.dao.assets import AssetsDao
from database.dao.users import UsersDao
from database.schemas.assets import AssetsSchema
from database.schemas.common import TgIdSchema
from general.exceptions import NotEnoughMoney
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

from states.game import GameFsm
from utils.pretty_text import make_build


class ShopManager(RouterHelper):

    async def show_assets(
        self,
    ):
        user = await UsersDao(
            session=self.session
        ).get_user_or_create(
            TgIdSchema(tg_id=self.callback.from_user.id)
        )
        resource_text = (
            f"💰Баланс: {user.balance}{MONEY_SYM}\n\n"
            f"🛍️Доступные ресурсы:\n\n"
            f"💌Анонимки: {user.anonymous_letters}\n\n"
            f"🛒️Выбери, что хочешь докупить"
        )
        markup = available_resources_kb()
        await self.callback.message.edit_text(
            text=make_build(resource_text), reply_markup=markup
        )

    async def select_number_of_resources(
        self,
        callback_data: ChooseToPurchaseCbData,
    ):
        resource = callback_data.resource
        user = await UsersDao(
            session=self.session
        ).get_user_or_create(
            TgIdSchema(tg_id=self.callback.from_user.id)
        )
        resource_count = getattr(user, resource.value)

        asset = await AssetsDao(
            session=self.session
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
        await self.callback.message.edit_text(
            text=make_build(text), reply_markup=markup
        )

    async def confirm_purchase_of_resource(
        self,
        callback_data: BuyResourcesCbData,
    ):
        asset_data = get_data_about_resource(
            resource=callback_data.resource
        )
        asset = await AssetsDao(
            session=self.session
        ).find_one_or_none(AssetsSchema(name=callback_data.resource))
        cost = get_cost_of_discounted_resource(
            cost=asset.cost, count=callback_data.count
        )
        message = (
            f"❗️Ты уверен, что хочешь купить «{asset_data.name}» "
            f"в количестве {callback_data.count} шт за {cost}{MONEY_SYM}?"
        )
        callback_data.is_confirmed = True
        await self.callback.message.edit_text(
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

    async def buy_resources(
        self,
        callback_data: BuyResourcesCbData,
    ):
        current_state = await self.state.get_state()
        if current_state == GameFsm.WAIT_FOR_STARTING_GAME.state:
            await self.callback.answer(
                "❌Во время регистрацию в игру нельзя покупать ресурсы",
                show_alert=True,
            )
            return
        asset = await AssetsDao(
            session=self.session
        ).find_one_or_none(AssetsSchema(name=callback_data.resource))
        cost = get_cost_of_discounted_resource(
            cost=asset.cost, count=callback_data.count
        )
        try:
            await UsersDao(session=self.session).update_assets(
                tg_id=TgIdSchema(tg_id=self.callback.from_user.id),
                asset=Resources[callback_data.resource],
                count=callback_data.count,
                cost=cost,
            )
        except NotEnoughMoney as e:
            await self.callback.answer(
                "❌Недостаточно средств на счету!\n\n"
                f"Текущий баланс: {e.balance}{MONEY_SYM}\n\n"
                f"Требуемая сумма к оплате: {cost}{MONEY_SYM}",
                show_alert=True,
            )
            return
        await self.callback.answer(
            f"✅Спасибо за покупку! С баланса списано {cost}{MONEY_SYM}",
            show_alert=True,
        )
        await self.show_assets()
