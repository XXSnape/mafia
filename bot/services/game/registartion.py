from aiogram import Dispatcher
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.payload import decode_payload

from cache.cache_types import (
    GameCache,
    LivePlayersIds,
    UserCache,
    UserGameCache,
    UsersInGame,
)
from database.dao.users import UsersDao
from database.schemas.roles import UserId
from keyboards.inline.keypads.join import get_join_kb
from services.base import RouterHelper
from states.states import GameFsm
from utils.utils import (
    get_profile_link,
    get_state_and_assign,
    get_profiles_during_registration,
    make_build,
)


class Registration(RouterHelper):
    async def _check_user_for_existence(self):
        user_id = self._get_user_id()
        users_dao = UsersDao(session=self.session)
        user = await users_dao.find_one_or_none(
            UserId(tg_id=user_id)
        )
        if user is None:
            await users_dao.add(UserId(tg_id=user_id))

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
        await self._init_game(message_id=sent_message.message_id)
        await sent_message.pin()

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
            else:
                await self.message.answer(
                    "Ты уже успешно зарегистрировался!"
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
        await self._check_user_for_existence()
        user_data: UserCache = {"game_chat": game_chat}
        await self.state.set_data(user_data)
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
        text = get_profiles_during_registration(
            game_data["players_ids"], game_data["players"]
        )
        await game_state.set_data(game_data)
        await self.message.answer("Ты в игре! Удачи!")
        markup = await get_join_kb(
            bot=bot,
            game_chat=game_chat,
            players_ids=game_data["players_ids"],
        )
        await bot.edit_message_text(
            chat_id=game_chat,
            text=text,
            message_id=game_data["start_message_id"],
            reply_markup=markup,
        )

    async def _init_game(self, message_id: int):
        game_data: GameCache = {
            "game_chat": self.message.chat.id,
            # "owner": self.message.from_user.id,
            "pros": [],
            "cons": [],
            "start_message_id": message_id,
            "players_ids": [],
            "players": {},
            "messages_after_night": [],
            "forged_roles": [],
            "winners": [],
            "losers": [],
            "to_delete": [],
            "vote_for": [],
            "tracking": {},
            "text_about_checks": "",
            # 'wait_for': [],
            "number_of_night": 0,
        }
        await self.state.set_data(game_data)
        await self.state.set_state(GameFsm.REGISTRATION)


async def add_user_to_game(
    dispatcher: Dispatcher,
    tg_obj: CallbackQuery | Message,
    state: FSMContext,
) -> tuple[LivePlayersIds, UsersInGame]:
    if isinstance(tg_obj, CallbackQuery):
        chat_id = tg_obj.message.chat.id
    else:
        chat_id = tg_obj.chat.id
    user_state: FSMContext = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=tg_obj.from_user.id,
        bot_id=tg_obj.bot.id,
    )
    user_data: UserCache = {"game_chat": chat_id}
    await user_state.update_data(user_data)
    game_data: GameCache = await state.get_data()
    user_game_data: UserGameCache = {
        "full_name": tg_obj.from_user.full_name,
        "url": get_profile_link(
            user_id=tg_obj.from_user.id,
            full_name=tg_obj.from_user.full_name,
        ),
        "money": 0,
        "achievements": [],
    }
    game_data["players_ids"].append(tg_obj.from_user.id)
    game_data["players"][str(tg_obj.from_user.id)] = user_game_data
    await state.set_data(game_data)
    return game_data["players_ids"], game_data["players"]
