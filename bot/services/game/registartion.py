import time
from dataclasses import dataclass
from datetime import timedelta, datetime, timezone
from pprint import pprint

from aiogram import Dispatcher
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.payload import decode_payload
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from cache.cache_types import (
    GameCache,
    UserCache,
    UserGameCache,
    OwnerCache,
    RolesLiteral,
    RolesAndUsersMoney,
)
from constants.output import MONEY_SYM
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.dao.users import UsersDao
from database.schemas.roles import UserId, UserTgId
from general.collection_of_roles import (
    get_data_with_roles,
    BASES_ROLES,
)
from keyboards.inline.keypads.join import (
    get_join_kb,
    offer_to_place_bet,
    cancel_bet,
)
from services.base import RouterHelper
from services.game.actions_at_night import get_game_state_and_data
from services.game.pipeline_game import Game
from services.settings.order_of_roles import RoleManager
from states.states import GameFsm
from utils.scheduler import (
    start_game,
    remind_of_beginning_of_game,
    clearing_tasks_on_schedule,
)
from utils.utils import (
    get_profile_link,
    get_state_and_assign,
    get_profiles_during_registration,
    make_build,
)


class Registration(RouterHelper):

    async def _get_user_or_create(self):
        user_id = self._get_user_id()
        users_dao = UsersDao(session=self.session)
        user = await users_dao.find_one_or_none(
            UserId(tg_id=user_id)
        )
        if user is None:
            user = await users_dao.add(UserId(tg_id=user_id))
        return user

    async def _get_user_balance(self):
        user = await self._get_user_or_create()
        return user.balance

    async def start_registration(self):
        await self.message.delete()
        markup = await get_join_kb(
            bot=self._get_bot(),
            game_chat=self.message.chat.id,
            players_ids=[],
        )
        sent_message = await self.message.answer(
            get_profiles_during_registration(
                live_players_ids=[], players={}
            ),
            reply_markup=markup,
        )
        start_of_registration_dt = datetime.utcnow()
        end_of_registration = int(
            (
                start_of_registration_dt + timedelta(seconds=40)
            ).timestamp()
        )
        start_of_registration = int(
            start_of_registration_dt.timestamp()
        )
        await self._init_game(
            message_id=sent_message.message_id,
            start_of_registration=start_of_registration,
            end_of_registration=end_of_registration,
        )
        await sent_message.pin()
        self.scheduler.add_job(
            func=start_game,
            trigger=DateTrigger(
                run_date=datetime.fromtimestamp(end_of_registration),
                timezone=timezone.utc,
            ),
            id=f"start_{self.message.chat.id}",
            kwargs={
                "message": sent_message,
                "state": self.state,
                "dispatcher": self.dispatcher,
                "scheduler": self.scheduler,
            },
            replace_existing=True,
        )
        self.scheduler.add_job(
            func=remind_of_beginning_of_game,
            trigger=IntervalTrigger(seconds=7),
            id=f"remind_{self.message.chat.id}",
            kwargs={"bot": self.message.bot, "state": self.state},
            replace_existing=True,
        )

    async def _offer_bet(self, game_data: GameCache, balance: int):
        to_user_markup = await offer_to_place_bet(
            banned_roles=game_data["owner"]["banned_roles"]
        )
        text = make_build(
            f"Ты в игре! Удачи! Твой баланс: {balance}. Если хочешь, можешь сделать ставку на разрешенную роль:\n\n"
        ) + RoleManager.get_current_order_text(
            selected_roles=game_data["owner"]["order_of_roles"]
        )

        if self.message:
            return await self.message.answer(
                text=text,
                reply_markup=to_user_markup,
            )
        await self.callback.message.edit_text(
            text=text,
            reply_markup=to_user_markup,
        )

    async def _change_message_in_group(
        self, game_data: GameCache, game_chat: int
    ):
        bot = self._get_bot()
        text = get_profiles_during_registration(
            game_data["players_ids"], game_data["players"]
        )
        to_group_markup = await get_join_kb(
            bot=bot,
            game_chat=game_chat,
            players_ids=game_data["players_ids"],
        )
        await bot.edit_message_text(
            chat_id=game_chat,
            text=text,
            message_id=game_data["start_message_id"],
            reply_markup=to_group_markup,
        )

    async def join_to_game(self, command: CommandObject):
        await self.message.delete()
        current_data: UserCache = await self.state.get_data()
        args = command.args
        game_chat = int(decode_payload(args))
        if "game_chat" in current_data:
            if current_data["game_chat"] != game_chat:
                await self.message.answer(
                    "Сначала заверши предыдущую игру"
                )
            return
        bot = self._get_bot()
        args = command.args
        game_chat = int(decode_payload(args))
        game_state = await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=game_chat,
            bot_id=bot.id,
        )
        current_game_state = await game_state.get_state()
        if current_game_state != GameFsm.REGISTRATION.state:
            await self.message.answer("Игра не может быть запущена!")
            return
        user_id = self._get_user_id()
        full_name = self.message.from_user.full_name
        game_data: GameCache = await game_state.get_data()
        balance = await self._get_user_balance()
        user_game_data: UserGameCache = {
            "full_name": full_name,
            "url": get_profile_link(
                user_id=user_id,
                full_name=full_name,
            ),
            "money": 0,
            "achievements": [],
        }
        game_data["players_ids"].append(user_id)
        game_data["players"][str(user_id)] = user_game_data
        # text = get_profiles_during_registration(
        #     game_data["players_ids"], game_data["players"]
        # )
        sent_message = await self._offer_bet(
            game_data=game_data, balance=balance
        )
        user_data: UserCache = {
            "game_chat": game_chat,
            "message_with_offer_id": sent_message.message_id,
        }
        await self.state.set_data(user_data)
        await self.state.set_state(GameFsm.WAIT_FOR_STARTING_GAME)
        game_data["to_delete"].append(
            [user_id, sent_message.message_id]
        )
        await game_state.set_data(game_data)
        await self._change_message_in_group(
            game_data=game_data, game_chat=game_chat
        )

    async def finish_registration(self):
        game_data: GameCache = await self.state.get_data()
        user_id = self._get_user_id()
        if game_data["owner"]["user_id"] != user_id:
            full_name = game_data["owner"]["full_name"]
            await self.callback.answer(
                f"Пожалуйста, попроси {full_name} начать игру!",
                show_alert=True,
            )
            return
        clearing_tasks_on_schedule(
            scheduler=self.scheduler,
            game_chat=game_data["game_chat"],
            is_running_on_schedule=False,
        )
        game = Game(
            message=self.callback.message,
            state=self.state,
            dispatcher=self.dispatcher,
            scheduler=self.scheduler,
        )
        await game.start_game()

    async def request_money(self):
        balance = await self._get_user_balance()
        role_key: RolesLiteral = self.callback.data
        coveted_role = get_data_with_roles(role_key)
        user_data: UserCache = {"coveted_role": role_key}
        await self.state.update_data(user_data)
        await self.callback.message.edit_text(
            text=f"Ты выбрал поставить на {coveted_role.role}. Твой баланс: {balance}."
            f"Введи сумму денег или отмени",
            reply_markup=cancel_bet(),
        )

    def _delete_bet(
        self, user_data: UserCache, game_data: GameCache
    ):
        index = None
        covered_roles = game_data["bids"].get(
            user_data.get("coveted_role"), []
        )
        if not covered_roles:
            return
        current_user_id = self._get_user_id()
        for cur_index, (user_id, _) in enumerate(covered_roles):
            if user_id == current_user_id:
                index = cur_index
                break
        if index is not None:
            covered_roles.pop(index)

    async def cancel_bet(self):
        user_data: UserCache = await self.state.get_data()
        game_state, game_data = await get_game_state_and_data(
            callback=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        self._delete_bet(user_data=user_data, game_data=game_data)
        del user_data["coveted_role"]
        await self.state.set_data(user_data)
        await game_state.set_data(game_data)
        balance = await self._get_user_balance()
        await self._offer_bet(balance=balance, game_data=game_data)

    async def leave_game(self, command: CommandObject):
        await self.message.delete()
        user_data: UserCache = await self.state.get_data()
        args = command.args
        game_chat = int(decode_payload(args))
        if user_data["game_chat"] != game_chat:
            return
        user_id = self._get_user_id()
        bot = self._get_bot()
        game_state = await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=user_data["game_chat"],
            bot_id=self.message.bot.id,
        )
        game_data: GameCache = await game_state.get_data()
        game_data["players_ids"].remove(user_id)
        del game_data["players"][str(user_id)]
        self._delete_bet(user_data=user_data, game_data=game_data)
        await game_state.set_data(game_data)
        await self._change_message_in_group(
            game_data=game_data, game_chat=user_data["game_chat"]
        )
        await bot.delete_message(
            chat_id=user_id,
            message_id=user_data["message_with_offer_id"],
        )
        await self.state.clear()
        await self.message.answer(
            make_build("Ты успешно вышел из игры!")
        )

    async def set_bet(self):
        await self.message.delete()
        rate = int(self.message.text)
        balance = await self._get_user_balance()
        if rate > balance:
            return
        user_data: UserCache = await self.state.get_data()
        bot = self._get_bot()
        user_id = self._get_user_id()
        game_state = await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=user_data["game_chat"],
            bot_id=bot.id,
        )
        game_data: GameCache = await game_state.get_data()
        bids: RolesAndUsersMoney = game_data["bids"]
        bids.setdefault(user_data["coveted_role"], []).append(
            [user_id, rate]
        )
        role = get_data_with_roles(user_data["coveted_role"])
        await self.state.set_data(user_data)
        await game_state.set_data(game_data)
        await bot.edit_message_text(
            chat_id=user_id,
            text=make_build(
                f"Ты успешно поставил {self.message.text}{MONEY_SYM} на роль {role.role}!"
            ),
            reply_markup=cancel_bet(),
            message_id=user_data["message_with_offer_id"],
        )

    async def _init_game(
        self,
        message_id: int,
        start_of_registration: int,
        end_of_registration: int,
    ):
        owner_id = self._get_user_id()
        banned_roles = await ProhibitedRolesDAO(
            session=self.session
        ).get_keys_of_banned_roles(UserTgId(user_tg_id=owner_id))
        order_of_roles = await OrderOfRolesDAO(
            session=self.session
        ).get_key_of_order_of_roles(UserTgId(user_tg_id=owner_id))
        owner_data: OwnerCache = {
            "user_id": owner_id,
            "full_name": self.message.from_user.full_name,
            "order_of_roles": order_of_roles or BASES_ROLES,
            "banned_roles": banned_roles,
        }
        game_data: GameCache = {
            "game_chat": self.message.chat.id,
            "owner": owner_data,
            "pros": [],
            "cons": [],
            "start_message_id": message_id,
            "players_ids": [],
            "players": {},
            "messages_after_night": [],
            "to_delete": [],
            "vote_for": [],
            "tracking": {},
            "text_about_checks": "",
            "bids": {},
            "start_of_registration": start_of_registration,
            "end_of_registration": end_of_registration,
            # 'wait_for': [],
            "number_of_night": 0,
        }
        await self.state.set_data(game_data)
        await self.state.set_state(GameFsm.REGISTRATION)
