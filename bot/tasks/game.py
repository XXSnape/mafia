import asyncio

from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramAPIError,
)
from loguru import logger

from database.dao.games import GamesDao
from database.dao.rates import RatesDao
from database.dao.results import ResultsDao
from database.dao.subscriptions import SubscriptionsDAO
from database.dao.users import UsersDao
from database.schemas.bids import (
    BidForRoleSchema,
    ResultBidForRoleSchema,
)
from database.schemas.common import IdSchema
from database.schemas.games import EndOfGameSchema
from database.schemas.groups import GroupIdSchema
from database.schemas.results import PersonalResultSchema
from faststream import FastStream

from database.schemas.subscriptions import NotificationSchema
from general.collection_of_roles import get_data_with_roles
from general.config import bot, broker
from general.text import MONEY_SYM
from keyboards.inline.keypads.subscriptions import (
    newsletter_about_new_game,
)
from tasks.dependencies import SessionWithCommitDep
from utils.pretty_text import make_build
from utils.tg import checking_for_presence_in_group


@broker.subscriber("betting_results")
async def analyze_betting_results(
    bids: list[ResultBidForRoleSchema], session: SessionWithCommitDep
):
    messages = []
    roles_data = get_data_with_roles()
    schemas = []
    for bet in bids:
        role = roles_data[bet.role_id].pretty_role
        if bet.is_winner is True:
            message = (
                f"✅Твоя ставка {bet.money}{MONEY_SYM} на "
                f"{role} зашла!"
            )
        else:
            message = (
                f"🚫Твоя ставка {bet.money}{MONEY_SYM} на "
                f"{role} не зашла!"
            )
        messages.append((bet.user_tg_id, make_build(message)))
        schemas.append(bet)
    rates_dao = RatesDao(session=session)
    users_dao = UsersDao(session=session)
    await asyncio.gather(
        *[
            bot.send_message(
                chat_id=user_id, text=message, protect_content=True
            )
            for user_id, message in messages
        ],
        return_exceptions=True,
    )
    await rates_dao.add_many(schemas)
    for bet in bids:
        if bet.is_winner:
            await users_dao.update_balance(
                user_money=bet, add_money=False
            )


@broker.subscriber("role_outside_game")
async def report_role_outside_game(bids: list[BidForRoleSchema]):
    roles_data = get_data_with_roles()
    messages = [
        (
            bet.user_tg_id,
            make_build(
                f"🚫Твоя ставка {bet.money}{MONEY_SYM} на "
                f"{roles_data[bet.role_id].pretty_role} "
                f"не зашла! Роли нет в игре!"
            ),
        )
        for bet in bids
    ]
    await asyncio.gather(
        *[
            bot.send_message(
                chat_id=user_id, text=message, protect_content=True
            )
            for user_id, message in messages
        ],
        return_exceptions=True,
    )


@broker.subscriber("game_results")
async def save_game_results(
    game_result: EndOfGameSchema, session: SessionWithCommitDep
):
    dao = GamesDao(session=session)
    await dao.update(
        filters=IdSchema(id=game_result.id), values=game_result
    )


@broker.subscriber("personal_results")
async def save_personal_results(
    personal_results: list[PersonalResultSchema],
    session: SessionWithCommitDep,
):
    result_dao = ResultsDao(session=session)
    users_dao = UsersDao(session=session)
    await result_dao.add_many(personal_results, exclude={"text"})
    for result in personal_results:
        if result.money == 0:
            continue
        await users_dao.update_balance(
            user_money=result, add_money=True
        )


@broker.subscriber("refund_money_for_bets")
async def refund_money_for_bets(
    bids: list[BidForRoleSchema],
    session: SessionWithCommitDep,
):
    roles_data = get_data_with_roles()
    messages_to_users_tasks = []
    updates_tasks = []
    users_dao = UsersDao(session=session)
    for bet in bids:
        current_role = roles_data[bet.role_id]
        messages_to_users_tasks.append(
            bot.send_message(
                chat_id=bet.user_tg_id,
                text=make_build(
                    f"Возвращены {bet.money}{MONEY_SYM} "
                    f"за ставку на {current_role.pretty_role}"
                ),
            )
        )
        updates_tasks.append(
            users_dao.update_balance(user_money=bet, add_money=True)
        )
    await asyncio.gather(*updates_tasks)
    await asyncio.gather(
        *messages_to_users_tasks, return_exceptions=True
    )


@broker.subscriber("notifications_of_start_of_new_game")
async def notify_of_start_of_new_game(
    notification: NotificationSchema,
    session: SessionWithCommitDep,
):
    subscriptions_dao = SubscriptionsDAO(session=session)
    subscribed_people = await subscriptions_dao.find_all(
        GroupIdSchema(group_id=notification.group_id)
    )
    markup = await newsletter_about_new_game(
        bot=bot,
        game_chat=notification.game_chat,
        group_id=notification.group_id,
    )
    text = make_build(
        f"❗️В группе «{notification.title}» начинается новая игра!"
    )
    to_delete = set[int]()
    for subscription in subscribed_people:
        try:
            await bot.send_message(
                chat_id=subscription.user_tg_id,
                text=text,
                reply_markup=markup,
            )
        except TelegramForbiddenError:
            to_delete.add(subscription.id)
        except Exception as e:
            logger.exception(
                "Ошибка при отправке уведомления о начале игры"
            )
    for subscription in subscribed_people:
        try:
            result = await checking_for_presence_in_group(
                bot=bot,
                chat_id=notification.game_chat,
                user_id=subscription.user_tg_id,
            )
            if result is False:
                to_delete.add(subscription.id)
        except TelegramAPIError as e:
            logger.exception(
                "Ошибка при проверке наличия пользователя в группе"
            )
    await subscriptions_dao.delete_subscriptions(ids=to_delete)


app = FastStream(broker)
