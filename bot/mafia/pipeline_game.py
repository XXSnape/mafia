import asyncio
import datetime
from operator import itemgetter
from pprint import pprint
from random import choice
from typing import Literal, cast

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.cache_types import (
    GameCache,
    RoleAndUserMoney,
    RolesLiteral,
    UserGameCache,
    UserIdStr,
)
from database.dao.games import GamesDao
from database.schemas.bids import (
    BidForRoleSchema,
    ResultBidForRoleSchema,
)
from database.schemas.common import IdSchema, TgIdSchema
from database.schemas.games import (
    EndOfGameSchema,
)
from database.schemas.results import PersonalResultSchema
from faststream.rabbit import RabbitBroker
from general.collection_of_roles import (
    BASES_ROLES,
    DataWithRoles,
    get_data_with_roles,
)
from general.exceptions import GameIsOver
from general.groupings import Groupings
from general.text import MONEY_SYM
from keyboards.inline.keypads.to_bot import get_to_bot_kb
from loguru import logger
from mafia.controlling_game import Controller
from mafia.roles import RoleABC, ActiveRoleAtNightABC
from services.common.settings import SettingsRouter
from sqlalchemy.ext.asyncio import AsyncSession
from states.game import GameFsm
from utils.informing import (
    get_profiles,
    send_a_lot_of_messages_safely,
)
from utils.pretty_text import (
    get_minutes_and_seconds_text,
    make_build,
)
from utils.sorting import sorting_by_money, sorting_by_rate
from utils.state import (
    lock_state,
    reset_user_state_if_in_game,
)
from utils.tg import (
    delete_messages_from_to_delete,
    resending_message,
    unban_users,
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
        self.all_roles: DataWithRoles = {}
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
        self.original_roles_in_fog_of_war: str | None = None

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
            tg_id=TgIdSchema(tg_id=self.group_chat_id),
            start=beginning_dt,
        )
        await self.session.commit()

    async def start_game(
        self,
    ):
        try:
            async with lock_state(self.state):
                current_game_state = await self.state.get_state()
                if current_game_state != GameFsm.REGISTRATION.state:
                    return
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
            self.init_existing_roles(game_data)
            await self.familiarize_players(game_data)
            await resending_message(
                bot=self.bot,
                chat_id=self.group_chat_id,
                text=make_build(
                    "🎲Игра начинается!\n\n⚙️Текущие настройки:\n\n"
                )
                + SettingsRouter.get_other_settings_text(
                    settings=game_data["settings"]
                ),
                reply_markup=get_to_bot_kb(),
            )
            while True:
                try:
                    await self.start_night()
                except GameIsOver as e:
                    await self.give_out_rewards(e=e)
                    return
        except Exception as e:
            logger.exception("Произошла ошибка во время игры")
            await self.crash_game()

    async def crash_game(self):
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
            text=make_build(
                "❌Извините, игра аварийно завершилась!"
            ),
            users=list(game_data["players"].keys())
            + [self.group_chat_id],
            protect_content=False,
        )
        await unban_users(
            bot=self.bot,
            chat_id=self.group_chat_id,
            users=game_data["cant_talk"],
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
        await self.controller.start_new_night()
        game_data = await self.controller.mailing()
        await self.background_scanning(
            seconds=game_data["settings"]["time_for_night"],
            at_night=True,
        )
        game_data = await delete_messages_from_to_delete(
            bot=self.bot, state=self.state
        )
        await asyncio.sleep(4)
        await self.controller.send_delay_messages(
            game_data=game_data, at_night=True
        )
        game_data = await self.controller.sum_up_after_night()
        await self.controller.start_discussions(game_data)
        await self.background_scanning(
            seconds=game_data["settings"]["time_for_day"]
        )
        await self.controller.suggest_vote()
        await self.background_scanning(
            seconds=game_data["settings"]["time_for_voting"],
            at_night=False,
        )
        game_data = await delete_messages_from_to_delete(
            bot=self.bot, state=self.state
        )
        await asyncio.sleep(4)
        await self.controller.send_delay_messages(
            game_data=game_data, at_night=False
        )
        result = await self.controller.confirm_final_aim()
        if result:
            await self.background_scanning(
                seconds=game_data["settings"][
                    "time_for_confirmation"
                ],
            )
        await delete_messages_from_to_delete(
            bot=self.bot,
            state=self.state,
        )
        await self.controller.sum_up_after_voting()
        await self.controller.removing_players()
        await self.controller.end_night()
        await asyncio.sleep(4)

    async def background_scanning(
        self, seconds: int, at_night: bool | None = None
    ):
        while seconds > 0:
            await asyncio.sleep(5)
            game_data: GameCache = await self.state.get_data()
            key = None
            if at_night is True:
                key = "waiting_for_action_at_night"
            elif at_night is False:
                key = "waiting_for_action_at_day"
            if (
                key
                and game_data["settings"][
                    "speed_up_nights_and_voting"
                ]
            ):
                key = cast(
                    Literal[
                        "waiting_for_action_at_night",
                        "waiting_for_action_at_day",
                    ],
                    key,
                )
                if not game_data[key]:
                    return
            if len(game_data["wish_to_leave_game"]) >= len(
                game_data["live_players_ids"]
            ) and set(game_data["wish_to_leave_game"]).issuperset(
                game_data["live_players_ids"]
            ):
                raise GameIsOver(winner=Groupings.civilians)
            seconds -= 5

    async def give_out_rewards(self, e: GameIsOver):
        await asyncio.sleep(1)
        game_data: GameCache = await self.state.get_data()
        result = make_build(
            f"🚩Игра завершена! Победившая группировка — {e.winner.value.name}\n\n"
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
            show_initial_roles=True,
            show_money=True,
            show_current_roles=True,
            if_there_are_no_players=make_build(
                "\n😲Де-факто нет победителей!"
            ),
            sorting_factory=sorting_by_money,
        )
        losers_text = make_build(
            "\n\n🚫Проигравшие:\n"
        ) + get_profiles(
            players_ids=losers,
            players=game_data["players"],
            show_initial_roles=True,
            show_money=True,
            show_current_roles=True,
        )
        end_of_game = datetime.datetime.now()
        message = get_minutes_and_seconds_text(
            start=self.beginning_game,
            end=int(end_of_game.timestamp()),
            message="⏰Игра длилась ",
        )
        await resending_message(
            bot=self.bot,
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
        await unban_users(
            bot=self.bot,
            chat_id=self.group_chat_id,
            users=game_data["cant_talk"],
        )
        await self.state.clear()

    async def sum_up_personal_results_players(
        self,
        user_id: UserIdStr,
        player_data: UserGameCache,
        personal_results: dict[UserIdStr, PersonalResultSchema],
    ):
        await reset_user_state_if_in_game(
            dispatcher=self.dispatcher,
            user_id=int(user_id),
            bot_id=self.bot.id,
            group_id=self.group_chat_id,
        )
        achievements = player_data["achievements"]
        result = personal_results[user_id]
        messages = []
        text = result.text
        if not achievements:
            text += make_build(
                "\nℹ️У тебя нет полезных действий за игру!"
            )
        else:
            text += make_build(
                "\nℹ️Отчет о действиях, повлиявших на исход:"
            )
            for achievement, money in achievements:
                current_text = achievement.format(
                    money=money if result.money != 0 else 0
                )
                if len(text) > 3700:
                    messages.append(text)
                    text = f"● {current_text}"
                else:
                    text += f"\n\n● {current_text}"
        text += make_build(f"\n\nИтого: {result.money}{MONEY_SYM}")
        messages.append(text)
        for message in messages:
            await self.bot.send_message(
                chat_id=int(user_id), text=message
            )

    @staticmethod
    def initialization_by_role(game_data: GameCache, role: RoleABC):
        if (
            role.is_alias is False
            and role.roles_key not in game_data
        ):
            game_data[role.roles_key] = []
            if isinstance(role, ActiveRoleAtNightABC):
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
        if game_data["settings"]["allow_betting"] is False:
            return (
                {},
                [],
            )
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
        divider = 3 if game_data["settings"]["mafia_every_3"] else 4
        while len(order_of_roles) < number_of_players:
            if (len(order_of_roles) + 1) % divider == 0:
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
                "pretty_role": current_role.pretty_role,
                "initial_role": current_role.pretty_role,
                "role_id": role_id,
                "initial_role_id": role_id,
                "roles_key": current_role.roles_key,
            }
            game_data["players"][str(winner_id)].update(user_data)
            roles.append(winner_id)
        pprint(game_data)
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
        other_tasks = []
        for role in self.all_roles:
            current_role = self.all_roles[role]
            if current_role.is_alias:
                continue
            roles, aliases, other = (
                current_role.introducing_users_to_roles(game_data)
            )
            roles_tasks.extend(roles)
            aliases_tasks.extend(aliases)
            other_tasks.extend(other)
        await asyncio.gather(*roles_tasks, return_exceptions=True)
        await asyncio.gather(*aliases_tasks, return_exceptions=True)
        await asyncio.gather(*other_tasks, return_exceptions=True)
