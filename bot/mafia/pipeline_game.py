import asyncio
import datetime
from collections import defaultdict
from operator import itemgetter
from pprint import pprint
from random import choice

from aiogram import Dispatcher, Bot
from aiogram.fsm.context import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from cache.cache_types import (
    GameCache,
    UserGameCache,
    RolesLiteral,
    UserIdInt,
    RoleAndUserMoney,
    UserIdStr,
)
from database.schemas.common import TgId, IdSchema
from database.schemas.groups import GroupIdSchema
from general.text import MONEY_SYM
from database.dao.games import GamesDao
from database.schemas.bids import (
    BidForRoleSchema,
    ResultBidForRoleSchema,
)
from database.schemas.games import (
    BeginningOfGameSchema,
    EndOfGameSchema,
)
from database.schemas.results import PersonalResultSchema
from general.collection_of_roles import (
    get_data_with_roles,
    BASES_ROLES,
)
from general.exceptions import GameIsOver
from general.groupings import Groupings

from keyboards.inline.keypads.to_bot import get_to_bot_kb
from mafia.controlling_game import Controller
from mafia.roles import RoleABC, Mafia, Forger, Traitor
from states.states import GameFsm
from utils.sorting import sorting_by_rate, sorting_by_money
from utils.tg import delete_messages_from_to_delete
from utils.state import (
    reset_user_state,
    get_state_and_assign,
    reset_user_state_if_in_game,
)
from utils.pretty_text import (
    make_pretty,
    make_build,
    get_minutes_and_seconds_text,
)
from utils.informing import (
    get_live_players,
    get_profiles,
    send_a_lot_of_messages_safely,
)


class Game:
    def __init__(
        self,
        bot: Bot,
        group_chat_id: int,
        state: FSMContext,
        dispatcher: Dispatcher,
        scheduler: AsyncIOScheduler,
        broker: RabbitBroker,
        session: AsyncSession,
    ):
        self.scheduler = scheduler
        self.state = state
        self.dispatcher = dispatcher
        self.bot = bot
        self.group_chat_id = group_chat_id
        self.all_roles = {}
        self.controller = Controller(
            bot=self.bot,
            group_chat_id=self.group_chat_id,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        self.broker = broker
        self.session = session
        self.game_id: int | None = None
        self.beginning_game: int | None = None
        self.winners_bets = []

    def init_existing_roles(self, game_data: GameCache):
        all_roles = get_data_with_roles()
        existing = set(
            player_data["role_id"]
            for player_data in game_data["players"].values()
        )
        not_existing = set(
            role for role in all_roles if role not in existing
        )
        for role in not_existing:
            all_roles.pop(role)
        self.all_roles = all_roles
        for role in self.all_roles:
            self.all_roles[role](
                dispatcher=self.dispatcher,
                bot=self.bot,
                state=self.state,
                all_roles=self.all_roles,
            )
        self.controller.all_roles = all_roles

    async def create_game_in_db(self):
        dao = GamesDao(session=self.session)
        beginning_dt = datetime.datetime.now()
        self.beginning_game = int(beginning_dt.timestamp())
        self.game_id = await dao.create_game(
            tg_id=TgId(tg_id=self.group_chat_id), start=beginning_dt
        )
        await self.session.commit()

    async def start_game(
        self,
    ):
        try:
            game_data: GameCache = await self.state.get_data()
            await asyncio.gather(
                delete_messages_from_to_delete(
                    bot=self.bot,
                    state=self.state,
                ),
                self.bot.delete_message(
                    chat_id=self.group_chat_id,
                    message_id=game_data["start_message_id"],
                ),
            )
            await self.create_game_in_db()
            await self.state.set_state(GameFsm.STARTED)
            game_data = await self.select_roles()
            await self.familiarize_players(game_data)
            self.init_existing_roles(game_data)
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text=make_build("Игра начинается!"),
                reply_markup=get_to_bot_kb(),
            )
            while True:
                try:
                    await self.start_night()
                except GameIsOver as e:
                    await self.give_out_rewards(e=e)
                    return
        except Exception as e:
            await self.crash_game(e=e)

    async def crash_game(self, e: Exception):
        logger.error("Произошла ошибка во время игры {}", e)
        game_data: GameCache = await self.state.get_data()
        await delete_messages_from_to_delete(
            bot=self.bot,
            state=self.state,
        )
        await asyncio.gather(
            *(
                reset_user_state_if_in_game(
                    dispatcher=self.dispatcher,
                    user_id=int(user_id),
                    bot_id=self.bot.id,
                    group_id=self.group_chat_id,
                )
                for user_id in game_data["players"]
            )
        )
        await send_a_lot_of_messages_safely(
            bot=self.bot,
            text=make_build("Извините, игра аварийно завершилась!"),
            users=list(game_data["players"].keys())
            + [self.group_chat_id],
        )
        await self.state.clear()
        if self.game_id:
            dao = GamesDao(session=self.session)
            await dao.delete(IdSchema(id=self.game_id))
        await self.broker.publish(
            message=self.winners_bets, queue="refund_money_for_bets"
        )

    async def start_night(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        game_data["number_of_night"] += 1
        await self.state.set_data(game_data)
        players = get_live_players(
            game_data=game_data, all_roles=self.all_roles
        )
        night_starts_text = make_build(
            f"Наступает ночь {game_data['number_of_night']}"
        )
        message = await self.bot.send_photo(
            chat_id=self.group_chat_id,
            photo="https://i.pinimg.com/originals/f0/43/ed/f043edcac9690fdec845925508006459.jpg",
            caption=f"{night_starts_text}.\n\n{players}",
            reply_markup=get_to_bot_kb("Действовать!"),
        )
        await message.pin()
        await self.controller.mailing()
        await asyncio.sleep(32)
        await delete_messages_from_to_delete(
            bot=self.bot,
            state=self.state,
        )
        game_data = await self.controller.sum_up_after_night()
        players_after_night = get_live_players(
            game_data=game_data, all_roles=self.all_roles
        )
        await self.bot.send_photo(
            chat_id=self.group_chat_id,
            photo="https://i.pinimg.com/originals/b1/80/98/b18098074864e4b1bf5cc8412ced6421.jpg",
            caption=f"{make_build('Пришло время провести следственные мероприятия жителям города!')}\n\n"
            f"{players_after_night}",
        )
        await asyncio.sleep(4)
        await self.controller.suggest_vote()
        await asyncio.sleep(15)
        await delete_messages_from_to_delete(
            bot=self.bot,
            state=self.state,
        )
        result = await self.controller.confirm_final_aim()
        if result:
            await asyncio.sleep(12)
        await delete_messages_from_to_delete(
            bot=self.bot,
            state=self.state,
        )
        await self.controller.sum_up_after_voting()
        await self.controller.removing_inactive_players()
        await self.controller.end_night()

    async def give_out_rewards(self, e: GameIsOver):
        game_data: GameCache = await self.state.get_data()
        result = make_build(
            f"🚩Игра завершена! Победившая группировка: {e.winner.value.name}\n\n"
        )
        winners = []
        losers = []
        personal_results: dict[UserIdStr, PersonalResultSchema] = {}
        for user_id, player in game_data["players"].items():
            role_id = player["role_id"]
            current_role: RoleABC = self.all_roles[role_id]
            personal_result = current_role.earn_money_for_winning(
                winning_group=e.winner,
                game_data=game_data,
                user_id=user_id,
                game_id=self.game_id,
            )
            if personal_result.is_winner:
                winners.append(user_id)
            else:
                losers.append(user_id)
            personal_results[user_id] = personal_result
        winners_text = make_build("🔥Победители:\n") + get_profiles(
            players_ids=winners,
            players=game_data["players"],
            initial_role=True,
            money_need=True,
            role=True,
            if_there_are_no_players="Де-факто нет победителей!",
            sorting_factory=sorting_by_money,
        )
        losers_text = make_build(
            "\n\n🚫Проигравшие:\n"
        ) + get_profiles(
            players_ids=losers,
            players=game_data["players"],
            initial_role=True,
            money_need=True,
            role=True,
        )
        end_of_game = datetime.datetime.now()
        message = get_minutes_and_seconds_text(
            start=self.beginning_game,
            end=int(end_of_game.timestamp()),
            message="⏰ Игра длилась ",
        )
        await self.bot.send_message(
            chat_id=self.group_chat_id,
            text=result
            + winners_text
            + losers_text
            + make_build(
                f"\n\n{message} Количество ночей: {game_data['number_of_night']}"
            ),
            reply_markup=get_to_bot_kb("К результатам!"),
        )
        await delete_messages_from_to_delete(
            bot=self.bot,
            state=self.state,
        )
        await self.broker.publish(
            message=EndOfGameSchema(
                id=self.game_id,
                number_of_nights=game_data["number_of_night"],
                end=end_of_game,
                winning_group=e.winner.value.name,
            ),
            queue="game_results",
        )
        await self.broker.publish(
            message=list(personal_results.values()),
            queue="personal_results",
        )
        await asyncio.gather(
            *(
                self.sum_up_personal_results_players(
                    user_id=user_id,
                    player_data=player_data,
                    personal_results=personal_results,
                )
                for user_id, player_data in game_data[
                    "players"
                ].items()
            ),
            return_exceptions=True,
        )
        await self.state.clear()

    async def sum_up_personal_results_players(
        self,
        user_id: UserIdStr,
        player_data: UserGameCache,
        personal_results: dict[UserIdStr, PersonalResultSchema],
    ):
        achievements = player_data["achievements"]
        result = personal_results[user_id]
        text = result.text
        if not achievements:
            achievements_text = make_build(
                "\nУ тебя нет полезных действий за игру!"
            )
        else:
            achievements_text = make_build(
                "\nОтчет о действиях, повлиявших на исход:\n\n● "
            ) + "\n\n● ".join(
                achievement.format(
                    money=money if result.money != 0 else 0
                )
                for achievement, money in achievements
            )
        text += achievements_text
        text += make_build(f"\n\nИтого: {result.money}{MONEY_SYM}")
        await self.bot.send_message(chat_id=int(user_id), text=text)
        await reset_user_state_if_in_game(
            dispatcher=self.dispatcher,
            user_id=int(user_id),
            bot_id=self.bot.id,
            group_id=self.group_chat_id,
        )

    @staticmethod
    def initialization_by_role(game_data: GameCache, role: RoleABC):
        if (
            role.is_alias is False
            and role.roles_key not in game_data
        ):
            game_data[role.roles_key] = []
            if role.processed_users_key:
                game_data[role.processed_users_key] = []
            if role.last_interactive_key:
                game_data[role.last_interactive_key] = {}
            if role.processed_by_boss:
                game_data[role.processed_by_boss] = []
            if role.extra_data:
                for extra in role.extra_data:
                    game_data[extra.key] = extra.data_type()

    @staticmethod
    def check_bids(
        game_data: GameCache,
    ) -> tuple[RoleAndUserMoney, list[BidForRoleSchema]]:
        role_and_winner_with_money: RoleAndUserMoney = {}
        bids = game_data["bids"]
        losers: list[BidForRoleSchema] = []
        for role_key, rates in bids.items():
            rates.sort(key=itemgetter(1), reverse=True)
            if len(rates) == 0:
                continue
            if len(rates) == 1:
                role_and_winner_with_money[role_key] = [
                    rates[0][0],
                    rates[0][1],
                ]
            elif rates[0][1] == rates[1][1]:
                for user_id, money in rates:
                    loser = BidForRoleSchema(
                        user_tg_id=user_id,
                        role_id=role_key,
                        money=money,
                    )
                    losers.append(loser)
            else:
                role_and_winner_with_money[role_key] = [
                    rates[0][0],
                    rates[0][1],
                ]
                for user_id, money in rates[1:]:
                    loser = BidForRoleSchema(
                        user_tg_id=user_id,
                        role_id=role_key,
                        money=money,
                    )
                    losers.append(loser)
        sorted_roles_and_winner = {}
        for role_key, winner in sorted(
            role_and_winner_with_money.items(),
            key=sorting_by_rate,
            reverse=True,
        ):
            sorted_roles_and_winner[role_key] = winner
        return sorted_roles_and_winner, losers

    async def record_data_about_betting_results(
        self,
        order_of_roles: list[RolesLiteral],
        winners_bets: list[BidForRoleSchema],
        losers_bets: list[BidForRoleSchema],
    ):
        rates = []
        roles_are_not_in_game = []
        self.winners_bets = winners_bets
        for winner in winners_bets:
            rates.append(
                ResultBidForRoleSchema(
                    **winner.model_dump(),
                    game_id=self.game_id,
                    is_winner=True,
                )
            )
        for loser in losers_bets:
            if loser.role_id in order_of_roles:
                rates.append(
                    ResultBidForRoleSchema(
                        **loser.model_dump(),
                        game_id=self.game_id,
                        is_winner=False,
                    )
                )
            else:
                roles_are_not_in_game.append(loser)
        await self.broker.publish(
            message=rates, queue="betting_results"
        )
        await self.broker.publish(
            message=roles_are_not_in_game, queue="role_outside_game"
        )

    async def select_roles(self):
        game_data: GameCache = await self.state.get_data()
        banned_roles = game_data["settings"]["banned_roles"]
        order_of_roles = game_data["settings"]["order_of_roles"]
        print("initial", order_of_roles)
        players_ids = game_data["live_players_ids"][:]
        all_roles = get_data_with_roles()
        criminals: list[RolesLiteral] = []
        other: list[RolesLiteral] = []
        number_of_players = len(players_ids)
        for key, role in all_roles.items():
            if (
                key in banned_roles
                or key in BASES_ROLES
                and role.there_may_be_several is False
            ):
                continue
            if role.grouping == Groupings.criminals:
                role_type = criminals
            else:
                role_type = other
            if role not in order_of_roles:
                role_type.append(key)
            elif get_data_with_roles(role).there_may_be_several:
                role_type.append(key)
        role_and_winner, losers = self.check_bids(game_data)
        not_winners = [loser.user_tg_id for loser in losers]
        winning_roles = list(
            role
            for role in role_and_winner.keys()
            if role not in order_of_roles
        )
        while len(order_of_roles) < number_of_players:
            if (
                len(order_of_roles) % 4 == 0
                and len(order_of_roles) != 4
            ):
                role_type = criminals
            else:
                role_type = other
            role = None
            for winning_role in winning_roles:
                if winning_role in role_type:
                    role = winning_role
                    break
            if role:
                winning_roles.remove(role)
            else:
                role = choice(role_type)
            order_of_roles.append(role)
            if (
                get_data_with_roles(role).there_may_be_several
                is False
            ):
                role_type.remove(role)
        winners = set()
        order_of_roles[:] = order_of_roles[:number_of_players]
        print("order", order_of_roles)
        for role_id, (winner_id, money) in role_and_winner.items():
            if role_id not in order_of_roles:
                not_winners.append(winner_id)
                losers.append(
                    BidForRoleSchema(
                        user_tg_id=winner_id,
                        role_id=role_id,
                        money=money,
                    )
                )
            else:
                winners.add(winner_id)
        not_winners.extend(
            set(players_ids) - (set(not_winners) | winners)
        )
        winners_bets: list[BidForRoleSchema] = []
        for number, role_id in enumerate(order_of_roles, 1):
            current_role = get_data_with_roles(role_id)
            winner = role_and_winner.get(role_id)
            if winner is None:
                winner_id = choice(not_winners)
                not_winners.remove(winner_id)
            else:
                winner_id = winner[0]
                role_and_winner.pop(role_id)
                winners_bets.append(
                    BidForRoleSchema(
                        user_tg_id=winner_id,
                        role_id=role_id,
                        money=winner[1],
                    )
                )
            self.initialization_by_role(game_data, role=current_role)
            roles = game_data[current_role.roles_key]
            user_data: UserGameCache = {
                "number": players_ids.index(winner_id) + 1,
                "pretty_role": make_pretty(current_role.role),
                "initial_role": make_pretty(current_role.role),
                "role_id": role_id,
                "initial_role_id": role_id,
                "roles_key": current_role.roles_key,
            }
            game_data["players"][str(winner_id)].update(user_data)
            roles.append(winner_id)
        await self.record_data_about_betting_results(
            order_of_roles=order_of_roles,
            winners_bets=winners_bets,
            losers_bets=losers,
        )
        await self.state.set_data(game_data)
        return game_data

    async def familiarize_players(self, game_data: GameCache):
        roles_tasks = []
        aliases_tasks = []
        to_criminals_messages = defaultdict(list)
        for user_id, player_data in game_data["players"].items():
            player_data: UserGameCache
            current_role = get_data_with_roles(
                player_data["role_id"]
            )
            if current_role.grouping == Groupings.criminals:
                roles = [Mafia, Forger, Traitor]
                for role in roles:
                    if role.roles_key != current_role.roles_key:
                        users = game_data.get(role.roles_key, [])
                        to_criminals_messages[int(user_id)].extend(
                            users
                        )

            if current_role.is_alias:
                continue
            persons = game_data[current_role.roles_key]
            roles_tasks.append(
                self.bot.send_photo(
                    chat_id=int(user_id),
                    photo=current_role.photo,
                    caption=f"Твоя роль - "
                    f"{make_pretty(current_role.role)}! "
                    f"{current_role.purpose}",
                )
            )
            if current_role.alias and len(persons) > 1:
                profiles = get_profiles(
                    players_ids=persons,
                    players=game_data["players"],
                    role=True,
                )
                aliases_tasks.append(
                    self.bot.send_message(
                        chat_id=persons[0],
                        text="Твои союзники:\n" + profiles,
                    )
                )
                for user_id in persons[1:]:
                    roles_tasks.append(
                        self.bot.send_photo(
                            chat_id=user_id,
                            photo=current_role.alias.photo,
                            caption=f"Твоя роль - "
                            f"{make_pretty(current_role.alias.role)}!"
                            f" {current_role.alias.purpose}",
                        )
                    )
                    aliases_tasks.append(
                        self.bot.send_message(
                            chat_id=user_id,
                            text="Твои союзники!\n\n" + profiles,
                        )
                    )
            if current_role.state_for_waiting_for_action:
                for person_id in persons:
                    roles_tasks.append(
                        get_state_and_assign(
                            dispatcher=self.dispatcher,
                            chat_id=person_id,
                            bot_id=self.bot.id,
                            new_state=current_role.state_for_waiting_for_action,
                        )
                    )
        await asyncio.gather(*roles_tasks, return_exceptions=True)
        await asyncio.gather(*aliases_tasks, return_exceptions=True)
        await asyncio.gather(
            *(
                self.bot.send_message(
                    chat_id=user_id,
                    text=make_build("❗️Сокомандники:\n")
                    + get_profiles(
                        players_ids=teammates,
                        players=game_data["players"],
                        role=True,
                    ),
                )
                for user_id, teammates in to_criminals_messages.items()
                if teammates
            ),
            return_exceptions=True,
        )
