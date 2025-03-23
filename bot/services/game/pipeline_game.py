import asyncio
from operator import itemgetter
from random import choice

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext

from aiogram.types import Message

from cache.cache_types import (
    GameCache,
    UserGameCache,
    RolesLiteral,
    UserIdInt,
    UserAndMoney,
)
from constants.output import MONEY_SYM
from general.collection_of_roles import Roles, get_data_with_roles
from general.exceptions import GameIsOver
from general.groupings import Groupings

from keyboards.inline.keypads.to_bot import get_to_bot_kb
from services.game.mailing import MailerToPlayers
from services.game.processing import Executor
from services.game.roles.base import Role
from states.states import GameFsm
from utils.sorting import sorting_by_rate, sorting_by_money
from utils.utils import (
    get_state_and_assign,
    make_pretty,
    make_build,
    get_profiles,
)
from utils.live_players import get_live_players


class Game:
    def __init__(
        self,
        message: Message,
        state: FSMContext,
        dispatcher: Dispatcher,
    ):

        self.message = message
        self.state = state
        self.dispatcher = dispatcher
        self.bot = message.bot
        self.group_chat_id = self.message.chat.id
        self.mailer = MailerToPlayers(
            state=self.state,
            bot=self.bot,
            dispatcher=self.dispatcher,
            group_chat_id=self.group_chat_id,
        )
        self.all_roles = {}
        self.executor = Executor(
            message=message,
            state=state,
            dispatcher=dispatcher,
            mailer=self.mailer,
        )

    def init_existing_roles(self, game_data: GameCache):
        all_roles = get_data_with_roles()
        existing = set(
            player_data["enum_name"]
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
            )
        self.mailer.all_roles = all_roles
        self.executor.all_roles = all_roles

    async def start_game(
        self,
    ):

        await self.message.delete()
        await self.state.set_state(GameFsm.STARTED)
        await self.select_roles()
        game_data: GameCache = await self.state.get_data()
        await self.mailer.familiarize_players(game_data)
        self.init_existing_roles(game_data)
        await self.message.answer(
            text="Игра начинается!",
            reply_markup=get_to_bot_kb(),
        )
        while True:
            try:
                await self.start_night()
            except GameIsOver as e:
                await self.give_out_rewards(e=e)
                return

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
        await self.message.answer_photo(
            photo="https://i.pinimg.com/originals/f0/43/ed/f043edcac9690fdec845925508006459.jpg",
            caption=f"{night_starts_text}.\n\n{players}",
            reply_markup=get_to_bot_kb("Действовать!"),
        )

        await self.mailer.mailing()
        await asyncio.sleep(27)
        await self.executor.delete_messages_from_to_delete(
            to_delete=game_data["to_delete"]
        )
        await self.executor.sum_up_after_night()
        players_after_night = get_live_players(
            game_data=game_data, all_roles=self.all_roles
        )
        await self.message.answer_photo(
            photo="https://i.pinimg.com/originals/b1/80/98/b18098074864e4b1bf5cc8412ced6421.jpg",
            caption=f"{make_build('Пришло время провести следственные мероприятия жителям города!')}\n\n"
            f"{players_after_night}",
        )
        await asyncio.sleep(1)
        await self.mailer.suggest_vote()
        await asyncio.sleep(5)
        await self.executor.delete_messages_from_to_delete(
            to_delete=game_data["to_delete"]
        )
        result = await self.executor.confirm_final_aim()
        if result:
            await asyncio.sleep(10)
        await self.executor.delete_messages_from_to_delete(
            to_delete=game_data["to_delete"]
        )
        await self.executor.sum_up_after_voting()
        await asyncio.sleep(2)
        await self.executor.clear_data_after_all_actions()

    async def give_out_rewards(self, e: GameIsOver):
        game_data: GameCache = await self.state.get_data()
        result = make_build(
            f"🚩Игра завершена! Победившая группировка: {e.winner.value.name}\n\n"
        )
        winners = []
        losers = []
        for user_id, player in game_data["players"].items():
            enum_name = player["enum_name"]
            current_role: Role = self.all_roles[enum_name]
            is_winner = current_role.earn_money_for_winning(
                winning_group=e.winner,
                game_data=game_data,
                user_id=user_id,
            )
            if is_winner:
                winners.append(user_id)
            else:
                losers.append(user_id)
        sorting_func = sorting_by_money(game_data=game_data)
        winners.sort(key=sorting_func, reverse=True)
        winners = make_build("🔥Победители:\n") + get_profiles(
            players_ids=winners,
            players=game_data["players"],
            initial_role=True,
            money_need=True,
            role=True,
        )
        losers = make_build("\n\n🚫Проигравшие:\n") + get_profiles(
            players_ids=losers,
            players=game_data["players"],
            initial_role=True,
            money_need=True,
            role=True,
        )
        await self.bot.send_message(
            chat_id=self.group_chat_id,
            text=result + winners + losers,
        )
        await self.executor.delete_messages_from_to_delete(
            to_delete=game_data["to_delete"]
        )
        await asyncio.gather(
            *(
                self.reset_state(
                    user_id=int(user_id),
                    player_data=player_data,
                )
                for user_id, player_data in game_data[
                    "players"
                ].items()
            )
        )
        await self.state.clear()

    async def reset_state(
        self,
        user_id: int,
        player_data: UserGameCache,
    ):
        result_of_game, *achivements = player_data["achievements"]
        money = player_data["money"]
        text = result_of_game
        if money != 0:
            if not achivements:
                achivements_text = make_build(
                    "\nУ тебя нет активных действий за игру!"
                )
            else:
                achivements_text = make_build(
                    "\nОтчет об активных действиях, повлиявших на исход:\n\n● "
                ) + "\n● ".join(
                    achievement for achievement in achivements
                )
            text += achivements_text
        text += make_build(
            f"\n\nИтого: {player_data['money']}{MONEY_SYM}"
        )
        await self.bot.send_message(chat_id=user_id, text=text)
        state = await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=user_id,
            bot_id=self.bot.id,
        )
        await state.clear()

    @staticmethod
    def initialization_by_role(game_data: GameCache, role: Role):
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
    def check_bids(game_data: GameCache):
        role_and_winner_with_money: dict[
            RolesLiteral, UserAndMoney
        ] = {}
        bids = game_data["bids"]
        losers: list[UserIdInt] = []
        for role, rates in bids.items():
            rates.sort(key=itemgetter(1), reverse=True)
            if len(rates) == 1:
                role_and_winner_with_money[role] = [
                    rates[0][0],
                    rates[0][1],
                ]
            elif rates[0][1] == rates[1][1]:
                for user_id, _ in rates:
                    losers.append(user_id)
            else:
                role_and_winner_with_money[role] = [
                    rates[0][0],
                    rates[0][1],
                ]
                for user_id, _ in rates[1:]:
                    losers.append(user_id)
        sorted_roles_and_winner = {}
        for role, winner in sorted(
            role_and_winner_with_money.items(),
            key=sorting_by_rate,
            reverse=True,
        ):
            sorted_roles_and_winner[role] = winner
        return sorted_roles_and_winner, losers

    async def select_roles(self):
        game_data: GameCache = await self.state.get_data()
        banned_roles = game_data["owner"]["banned_roles"]
        order_of_roles = game_data["owner"]["order_of_roles"]
        players_ids = game_data["players_ids"]
        all_roles = get_data_with_roles()
        criminals: list[RolesLiteral] = []
        other: list[RolesLiteral] = []
        number_of_players = len(players_ids)
        for key, role in all_roles.items():
            if key in banned_roles:
                continue
            if role.grouping == Groupings.criminals:
                role_type = criminals
            else:
                role_type = other
            if role not in order_of_roles:
                role_type.append(key)
            elif get_data_with_roles(role).there_may_be_several:
                role_type.append(key)
        role_and_winner, not_winners = self.check_bids(game_data)
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
        for role, winner in role_and_winner.items():
            if role not in order_of_roles:
                not_winners.append(winner[0])
            else:
                winners.add(winner[0])
        not_winners.extend(
            set(players_ids) - (set(not_winners) | winners)
        )
        for role_key in order_of_roles[:number_of_players]:
            winner = role_and_winner.get(role_key)
            if winner is None:
                winner_id = choice(not_winners)
                not_winners.remove(winner_id)
            else:
                winner_id = winner[0]
            current_role = get_data_with_roles(role_key)
            self.initialization_by_role(game_data, role=current_role)
            roles = game_data[current_role.roles_key]
            user_data: UserGameCache = {
                "role": current_role.role,
                "pretty_role": make_pretty(current_role.role),
                "initial_role": make_pretty(current_role.role),
                "enum_name": role_key,
                "roles_key": current_role.roles_key,
                "user_id": winner_id,
            }
            game_data["players"][str(winner_id)].update(user_data)
            roles.append(winner_id)
        await self.state.set_data(game_data)
