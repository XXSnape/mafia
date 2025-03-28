from faststream import FastStream
import asyncio

from database.dao.games import GamesDao
from database.dao.results import ResultsDao
from database.schemas.common import IdSchema
from database.schemas.games import EndOfGameSchema
from database.schemas.results import PersonalResultSchema
from tasks.dependencies import SessionWithCommitDep

from constants.output import MONEY_SYM
from database.dao.rates import RatesDao
from database.dao.users import UsersDao
from database.schemas.bids import (
    ResultBidForRoleSchema,
    RateSchema,
    BidForRoleSchema,
)
from general.collection_of_roles import get_data_with_roles
from general.config import broker, bot
from utils.utils import make_build


@broker.subscriber("betting_results")
async def analyze_betting_results(
    bids: list[ResultBidForRoleSchema], session: SessionWithCommitDep
):
    messages = []
    roles_data = get_data_with_roles()
    schemas = []
    for bet in bids:
        role = roles_data[bet.role_key].role
        if bet.is_winner is True:
            message = f"✅Твоя ставка {bet.money}{MONEY_SYM} на {role} зашла!"
        else:
            message = f"🚫Твоя ставка {bet.money}{MONEY_SYM} на {role} не зашла!"
        messages.append((bet.user_tg_id, make_build(message)))
        rate_schema = RateSchema(
            **bet.model_dump(exclude={"role_key"}), role=role
        )
        schemas.append(rate_schema)
    rates_dao = RatesDao(session=session)
    users_dao = UsersDao(session=session)
    await asyncio.gather(
        *[
            bot.send_message(chat_id=user_id, text=message)
            for user_id, message in messages
        ]
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
                f"🚫Твоя ставка {bet.money}{MONEY_SYM} на {roles_data[bet.role_key].role} не зашла! Роли нет в игре!"
            ),
        )
        for bet in bids
    ]
    await asyncio.gather(
        *[
            bot.send_message(chat_id=user_id, text=message)
            for user_id, message in messages
        ]
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
        await users_dao.update_balance(
            user_money=result, add_money=True
        )


async def main():
    app = FastStream(broker)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
