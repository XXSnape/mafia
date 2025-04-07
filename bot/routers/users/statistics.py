from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.rates import RatesDao
from database.dao.results import ResultsDao
from database.dao.users import UsersDao
from database.schemas.common import TgId, UserTgId
from general.collection_of_roles import get_data_with_roles
from general.text import MONEY_SYM
from utils.pretty_text import make_pretty, make_build

router = Router(name=__name__)


@router.message(Command("profile"))
async def get_my_profile(
    message: Message, session_without_commit: AsyncSession
):
    users_dao = UsersDao(session=session_without_commit)
    user = await users_dao.find_one_or_none(
        TgId(tg_id=message.from_user.id)
    )
    balance = user.balance
    results_dao = ResultsDao(session=session_without_commit)

    number_of_games = 0
    number_of_wins = 0
    number_of_nights = 0
    money_sum = 0

    result = await results_dao.get_results(
        user_tg_id=UserTgId(user_tg_id=message.from_user.id)
    )
    all_roles = get_data_with_roles()
    if not result:
        detailed_statistics = ""
    else:
        detailed_statistics = "\n\nℹ️Подробная статистика:\n\n"
        for num, row in enumerate(result, 1):
            number_of_games += row.number_of_games
            number_of_wins += row.is_winner_count
            number_of_nights += row.nights_lived_count
            money_sum += row.money_sum
            current_role = all_roles[row.role_id]
            text = (
                f"{num}) {make_pretty(current_role.role)}: выиграно {row.is_winner_count} из {row.number_of_games} "
                f"({int(row.is_winner_count / row.number_of_games * 100)}%) {row.money_sum}{MONEY_SYM}\n"
            )
            detailed_statistics += text

    total_percentage_of_wins = (
        f"({int(number_of_wins / number_of_games * 100)}%)"
        if number_of_games
        else ""
    )
    average_number_of_nights_spent = (
        int(number_of_nights / number_of_games)
        if number_of_games
        else "Нет информации"
    )
    result_text = (
        f"👤Профиль {message.from_user.full_name}\n\n"
        f"💰Текущий баланс: {balance}{MONEY_SYM}\n"
        f"🎮Всего игр: {number_of_games}\n"
        f"✌️Побед: {number_of_wins} {total_percentage_of_wins}\n"
        f"💤Среднее количество проживаемых ночей: {average_number_of_nights_spent}"
    )
    result_text += detailed_statistics
    rates_result = await RatesDao(
        session=session_without_commit
    ).get_results(
        user_tg_id=UserTgId(user_tg_id=message.from_user.id)
    )
    if rates_result.count:

        rates_text = (
            f"\n\n🎲Сделано ставок: {rates_result.count}\n"
            f"🎱Выиграно ставок: {rates_result.is_winner_count} "
            f"({int(rates_result.is_winner_count / rates_result.count * 100)}%)\n"
            f"⛔Потрачено на ставки: {rates_result.money}{MONEY_SYM}"
        )
        result_text += rates_text
    result_text += f"\n\n💲Всего заработано: {money_sum}{MONEY_SYM}"
    await message.answer(make_build(result_text))
