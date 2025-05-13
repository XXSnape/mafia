from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from database.dao.subscriptions import SubscriptionsDAO
from database.dao.users import UsersDao
from database.schemas.common import TgIdSchema
from database.schemas.subscriptions import SubscriptionSchema
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    opt_out_of_notifications_btn,
)
from keyboards.inline.callback_factory.subscriptions import (
    GameNotificationCbData,
)
from services.base import RouterHelper
from utils.pretty_text import make_build
from utils.tg import delete_message


class SubscriptionsRouter(RouterHelper):

    async def subscribe_or_unsubscribe_from_group(self):
        await delete_message(message=self.message)
        group = await self.get_group_or_create()
        user = await UsersDao(
            session=self.session
        ).get_user_or_create(
            TgIdSchema(tg_id=self.message.from_user.id)
        )
        subscriptions_dao = SubscriptionsDAO(session=self.session)
        subscription_schema = SubscriptionSchema(
            user_tg_id=user.tg_id,
            group_id=group.id,
        )
        result = await subscriptions_dao.find_one_or_none(
            subscription_schema
        )
        markup = None
        if result is None:
            await subscriptions_dao.add(subscription_schema)
            to_user = (
                f"✅Ты успешно подписался на рассылку в группе "
                f"«{self.message.chat.title}» при начале новой игры"
            )
            markup = generate_inline_kb(
                data_with_buttons=[
                    opt_out_of_notifications_btn(group_id=group.id)
                ]
            )

        else:
            await subscriptions_dao.delete(subscription_schema)
            to_user = (
                f"❌Ты отписался от рассылки в группе "
                f"«{self.message.chat.title}» при начале новой игры"
            )
        with suppress(TelegramAPIError):
            await self.message.bot.send_message(
                chat_id=user.tg_id,
                text=make_build(to_user),
                reply_markup=markup,
            )

    async def disable_notifications(
        self, callback_data: GameNotificationCbData
    ):
        await SubscriptionsDAO(session=self.session).delete(
            SubscriptionSchema(
                user_tg_id=self.callback.from_user.id,
                group_id=callback_data.group_id,
            )
        )
        await self.callback.answer(
            text="❌Уведомления о начале следующей игры отключены",
            show_alert=True,
        )
        await delete_message(message=self.callback.message)
