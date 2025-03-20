import asyncio
from random import shuffle

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.cache_types import GameCache, UserGameCache
from constants.output import MONEY_SYM
from general.collection_of_roles import Roles, get_data_with_roles
from general.exceptions import GameIsOver

from keyboards.inline.keypads.to_bot import get_to_bot_kb
from services.game.mailing import MailerToPlayers
from services.game.processing import Executor
from services.game.roles.base import Role
from states.states import GameFsm
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
        scheduler: AsyncIOScheduler,
    ):

        self.message = message
        self.state = state
        self.dispatcher = dispatcher
        self.scheduler = scheduler
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
            scheduler=scheduler,
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
        def sorting_winners_by_money(user_id: str):
            return game_data["players"][user_id]["money"]

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
        winners.sort(key=sorting_winners_by_money, reverse=True)
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

    def initialization_by_role(
        self, game_data: GameCache, role: Role
    ):
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

    async def select_roles(self):
        game_data: GameCache = await self.state.get_data()
        ids = game_data["players_ids"][:]
        shuffle(ids)
        roles_tpl = tuple(Roles)
        for user_id, role in zip(ids, roles_tpl):
            current_role: Role = role.value
            self.initialization_by_role(game_data, role=current_role)
            roles = game_data[current_role.roles_key]
            user_data: UserGameCache = {
                "role": current_role.role,
                "pretty_role": make_pretty(current_role.role),
                "initial_role": make_pretty(current_role.role),
                "enum_name": role.name,
                "roles_key": current_role.roles_key,
                "user_id": user_id,
            }
            game_data["players"][str(user_id)].update(user_data)
            roles.append(user_id)
        await self.state.set_data(game_data)
