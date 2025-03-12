import asyncio
from pprint import pprint
from random import shuffle

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.cache_types import GameCache, UserGameCache
from general.collection_of_roles import Roles, get_data_with_roles
from general.exceptions import GameIsOver
from services.roles.base.roles import Groupings

from keyboards.inline.keypads.to_bot import get_to_bot_kb
from services.mailing import MailerToPlayers
from services.processing import Executor
from services.roles.base import Role
from states.states import GameFsm
from utils.utils import (
    get_state_and_assign,
    make_pretty,
    make_build,
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
            for player_id, player_data in game_data[
                "players"
            ].items()
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
        await asyncio.sleep(24)
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
        await asyncio.sleep(4)
        await self.mailer.suggest_vote()
        await asyncio.sleep(10)
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
        result = f"Игра завершена! Победившая группировка: {e.winner.value}"
        winners = "\nПобедители:\n"
        losers = "\nПроигравшие:\n"
        neutral = "\nСтатус-кво"

        victory_bonus = {
            Groupings.civilians: 40,
            Groupings.criminals: 60,
            Groupings.killer: 100,
        }

        for user_id, player in game_data["players"].items():
            enum_name = player["enum_name"]
            current_role: Role = self.all_roles[enum_name]
            text = f'{player["url"]} - {player["initial_role"]}'
            is_winner = None
            if current_role.grouping == e.winner:
                is_winner = True
                player["money"] += victory_bonus[e.winner]
            elif current_role.grouping != Groupings.other:
                is_winner = False
                player["money"] = 0
            elif int(user_id) in game_data["winners"]:
                is_winner = True
            elif int(user_id) in game_data["losers"]:
                is_winner = False
            text += f' ({player["money"]}💵)\n\n'
            if is_winner:
                winners += text
            elif is_winner is False:
                losers += text
            else:
                neutral += text
            player["is_winner"] = is_winner
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
                    chat_id=int(user_id),
                    player_data=player,
                    count_of_nights=game_data["number_of_night"],
                )
                for user_id, player in game_data["players"].items()
            )
        )
        await self.state.clear()
        return

    async def reset_state(
        self,
        chat_id: int,
        player_data: UserGameCache,
        count_of_nights: int,
    ):
        nights_lived = f"Ночей прожито: {player_data.get('number_died_at_night', count_of_nights)} из {count_of_nights}\n"
        payments = f"Выплаты за игру: {player_data['money']}\n"
        common_text = nights_lived + payments
        win_or_not = {
            True: f"Поздравлю! Ты победил в роли {player_data['initial_role']}!\n",
            False: f"К сожалению, ты проиграл в роли {player_data['initial_role']}!\n",
            None: "Ты завершил игру в нейтральном статусе!\n",
        }
        text = win_or_not[player_data["is_winner"]] + common_text
        if (
            player_data["is_winner"] is True
            or player_data["is_winner"] is None
        ):
            achievements = "\n---".join(
                achievement
                for achievement in player_data["achievements"]
            )
            if achievements:
                text += f"Твои достижения за игру: {achievements}"
            else:
                text += "У тебя нет достижений за игру!"

        await self.bot.send_message(chat_id=chat_id, text=text)
        state = await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=chat_id,
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
