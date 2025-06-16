import asyncio
from html import escape

from database.dao.games import GamesDao
from database.dao.rates import RatesDao
from database.dao.results import ResultsDao
from database.dao.users import UsersDao
from database.schemas.common import TgIdSchema, UserTgIdSchema
from database.schemas.groups import GroupIdSchema
from general.collection_of_roles import get_data_with_roles
from general.text import MONEY_SYM
from keyboards.inline.keypads.shop import to_shop_kb
from services.base import RouterHelper
from utils.pretty_text import (
    get_minutes_and_seconds_text,
    get_profile_link,
    make_build,
    make_pretty,
)
from utils.tg import delete_message


class StatisticsRouter(RouterHelper):
    async def get_my_profile(self):
        await self.message.delete()
        users_dao = UsersDao(session=self.session)
        user_tg_id_schema = UserTgIdSchema(
            user_tg_id=self.message.from_user.id
        )
        user = await users_dao.get_user_or_create(
            tg_id=TgIdSchema(tg_id=self.message.from_user.id)
        )
        balance = user.balance
        results_dao = ResultsDao(session=self.session)

        number_of_games = 0
        number_of_wins = 0
        number_of_nights = 0
        money_sum = 0

        result = await results_dao.get_results(
            user_tg_id=user_tg_id_schema
        )
        all_roles = get_data_with_roles()
        if not result:
            detailed_statistics = "\n\n"
        else:
            detailed_statistics = "\n\nℹ️Подробная статистика:\n\n"
            for num, row in enumerate(result, 1):
                number_of_games += row.number_of_games
                number_of_wins += row.is_winner_count
                number_of_nights += row.nights_lived_count
                money_sum += row.money_sum
                current_role = all_roles[row.role_id]
                text = (
                    f"{num}) {current_role.pretty_role}: "
                    f"выиграно {row.is_winner_count} из {row.number_of_games} "
                    f"({int(row.efficiency)}%) {row.money_sum}{MONEY_SYM}\n\n"
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
            f"👤Профиль {escape(self.message.from_user.full_name)}\n\n"
            f"💰Текущий баланс: {balance}{MONEY_SYM}\n"
            f"🎮Всего игр: {number_of_games}\n"
            f"✌️Побед: {number_of_wins} {total_percentage_of_wins}\n"
            f"💤Среднее количество проживаемых ночей: {average_number_of_nights_spent}"
        )
        result_text += detailed_statistics
        rates_result = await RatesDao(
            session=self.session
        ).get_results(user_tg_id=user_tg_id_schema)
        if rates_result.count:
            rates_text = (
                f"🎲Сделано ставок: {rates_result.count}\n"
                f"🎱Выиграно ставок: {rates_result.is_winner_count} "
                f"({int(rates_result.is_winner_count / rates_result.count * 100)}%)\n"
                f"⛔Потрачено на ставки: {rates_result.money}{MONEY_SYM}\n\n"
            )
            result_text += rates_text
        result_text += f"💲Всего заработано: {money_sum}{MONEY_SYM}"
        await self.message.answer(
            make_build(result_text),
            reply_markup=to_shop_kb(),
        )

    @staticmethod
    def sorting_by_efficiency(rows):
        n = 1
        is_sorted = False
        while not is_sorted:
            is_sorted = True
            for i in range(len(rows) - n):
                if (
                    abs(
                        rows[i].number_of_games
                        - rows[i + 1].number_of_games
                    )
                    <= 8
                    and rows[i + 1].efficiency > rows[i].efficiency
                ):
                    rows[i], rows[i + 1] = rows[i + 1], rows[i]
                    is_sorted = False
            n += 1

    async def get_group_statistics(self):
        await delete_message(self.message)
        group = await self.get_group_or_create()
        group_id_filter = GroupIdSchema(group_id=group.id)
        games_dao = GamesDao(session=self.session)
        game_result = await games_dao.get_results(group_id_filter)
        if game_result is None:
            await self.message.answer(
                make_build("В этой группе еще не было игр!")
            )
            return
        number_of_players = (
            await games_dao.get_average_number_of_players(
                group_id_filter
            )
        )
        minutes_and_seconds = get_minutes_and_seconds_text(
            seconds=int(game_result.average_time.total_seconds()),
            message="",
        )
        text = (
            "📈Статистика группы\n\n"
            f"🎮Количество игр: {game_result.number_of_games}\n"
            f"👤Среднее количество игроков за игру: {number_of_players}\n"
            f"💤Среднее количество ночей: {game_result.nights_lived_count}\n"
            f"⏰Cредняя продолжительность одной игры: {minutes_and_seconds}"
        )
        groupings_text = "\n\n👨‍👨‍👦‍👦Информация о группировках:\n\n"
        groupings_result = await games_dao.get_winning_groupings(
            group_id_filter
        )
        for num, row in enumerate(groupings_result, 1):
            winner_text = f"{num}) {make_pretty(row.winning_group)} - {row.number_of_wins} побед\n"
            groupings_text += winner_text
        text += groupings_text

        users_result = (
            await games_dao.get_statistics_of_players_by_group(
                group_id_filter
            )
        )
        self.sorting_by_efficiency(users_result)
        users_info = await asyncio.gather(
            *(
                self.message.bot.get_chat_member(
                    chat_id=self.message.chat.id,
                    user_id=row.user_tg_id,
                )
                for row in users_result
            ),
            return_exceptions=True,
        )
        users_text = "\n📊Топ 15 игроков за последний месяц:\n\n"
        for num, (user_info, user_data) in enumerate(
            zip(users_info, users_result), 1
        ):
            link = get_profile_link(
                user_id=user_data.user_tg_id,
                full_name=user_info.user.full_name,
            )
            user_stat = (
                f"{num}) {link}: выиграно {user_data.number_of_wins} "
                f"из {user_data.number_of_games} "
                f"({user_data.efficiency}%)\n"
            )
            users_text += user_stat
        text += users_text
        await self.message.answer(make_build(text))
