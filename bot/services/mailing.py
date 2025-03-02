import asyncio
from collections.abc import Iterable
from typing import Literal

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from cache.cache_types import (
    GameCache,
    RolesKeysLiteral,
    LivePlayersIds,
    UsersInGame,
    Roles,
)
from keyboards.inline.callback_factory.recognize_user import (
    UserVoteIndexCbData,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from keyboards.inline.keypads.to_bot import (
    get_to_bot_kb,
    participate_in_social_life,
)
from states.states import UserFsm
from utils.utils import make_pretty, get_state_and_assign


async def familiarize_players(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    mafias = game_data["mafias"]
    doctors = game_data["doctors"]
    policeman = game_data["policeman"]
    civilians = game_data["civilians"]
    lawyers = game_data["lawyers"]
    prosecutors = game_data["prosecutors"]
    masochists = game_data["masochists"]
    lucky_guys = game_data["lucky_guys"]
    suicide_bombers = game_data["suicide_bombers"]
    for user_id in mafias:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://i.pinimg.com/736x/a1/10/db/a110db3eaba78bf6423bcea68f330a64.jpg",
            caption=f"Твоя роль - {make_pretty(Roles.mafia)}! Тебе нужно уничтожить всех горожан.",
        )
    for user_id in doctors:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://gipermed.ru/upload/iblock/4bf/4bfa55f59ceb538bd2c8c437e8f71e5a.jpg",
            caption=f"Твоя роль - {make_pretty(Roles.doctor)}! Тебе нужно стараться лечить тех, кому нужна помощь.",
        )
    for user_id in policeman:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://avatars.mds.yandex.net/get-kinopoisk-image/1777765/59ba5e74-7a28-47b2-944a-2788dcd7ebaa/1920x",
            caption=f"Твоя роль - {make_pretty(Roles.policeman)}! Тебе нужно вычислить мафию.",
        )
    for user_id in lawyers:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://avatars.mds.yandex.net/get-altay/5579175/2a0000017e0aa51c3c1fd887206b0156ee34/XXL_height",
            caption=f"Твоя роль - {make_pretty(Roles.lawyer)}! Тебе нужно защитить мирных жителей от своих же на голосовании.",
        )
    for user_id in prosecutors:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://avatars.mds.yandex.net/i?id=b5115d431dafc24be07a55a8b6343540_l-5205087-images-thumbs&n=13",
            caption=f"Твоя роль - {make_pretty(Roles.prosecutor)}! Тебе нельзя допустить, чтобы днем мафия могла говорить.",
        )
    for user_id in civilians:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://cdn.culture.ru/c/820179.jpg",
            caption=f"Твоя роль - {make_pretty(Roles.civilian)}! Тебе нужно вычислить мафию на голосовании.",
        )
    for user_id in masochists:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://i.pinimg.com/736x/14/a5/f5/14a5f5eb5dbd73c4707f24d436d80c0b.jpg",
            caption=f"Твоя роль - {make_pretty(Roles.masochist)}! Тебе нужно умереть на дневном голосовании.",
        )
    for user_id in lucky_guys:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://avatars.mds.yandex.net/get-mpic/5031100/img_id5520953584482126492.jpeg/orig",
            caption=f"Твоя роль - {make_pretty(Roles.lucky_gay)}! "
            f"Возможно тебе повезет и ты останешься жив после покушения.",
        )
    for user_id in suicide_bombers:
        await bot.send_photo(
            chat_id=user_id,
            photo="https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
            "size=1280x1280&quality=96&"
            "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
            "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album",
            caption=f"Твоя роль - {make_pretty(Roles.suicide_bomber)}! "
            f"Тебе нужно умереть ночью.",
        )


class MailerToPlayers:
    def __init__(
        self,
        state: FSMContext,
        bot: Bot,
        dispatcher: Dispatcher,
        group_chat_id: int,
    ):
        self.state = state
        self.bot = bot
        self.dispatcher = dispatcher
        self.group_chat_id = group_chat_id

    async def _mail_user(
        self,
        text: str,
        role_key: RolesKeysLiteral,
        new_state: State,
        exclude: Iterable[int] | int = (),
    ):
        game_data: GameCache = await self.state.get_data()
        roles = game_data[role_key]
        role_id = roles[0]
        players = game_data["players"]
        markup = send_selection_to_players_kb(
            players_ids=game_data["players_ids"],
            players=players,
            exclude=exclude,
        )
        sent_survey = await self.bot.send_message(
            chat_id=role_id,
            text=text,
            reply_markup=markup,
        )
        game_data["to_delete"].append(
            [role_id, sent_survey.message_id]
        )
        await self.state.set_data(game_data)
        await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=role_id,
            bot_id=self.bot.id,
            new_state=new_state,
        )

    async def mail_prosecutor(self):
        game_data: GameCache = await self.state.get_data()
        prosecutors = game_data["prosecutors"]
        prosecutor_id = prosecutors[0]
        exclude = (
            []
            if game_data["last_arrested"] == 0
            else [game_data["last_arrested"]]
        )
        await self._mail_user(
            text="Кого арестовать этой ночью?",
            role_key="prosecutors",
            new_state=UserFsm.PROSECUTOR_ARRESTS,
            exclude=[prosecutor_id] + exclude,
        )

    async def mail_lawyer(self):
        game_data: GameCache = await self.state.get_data()
        exclude = (
            []
            if game_data["last_protected"] == 0
            else game_data["last_protected"]
        )
        await self._mail_user(
            text="Кого защитить на голосовании?",
            role_key="lawyers",
            new_state=UserFsm.LAWYER_PROTECTS,
            exclude=exclude,
        )

    async def mail_mafia(self):
        game_data: GameCache = await self.state.get_data()
        mafias = game_data["mafias"]
        mafia_id = mafias[0]
        await self._mail_user(
            text="Кого убить этой ночью?",
            role_key="mafias",
            new_state=UserFsm.MAFIA_ATTACKS,
            exclude=mafia_id,
        )

    async def mail_doctor(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        exclude = (
            []
            if game_data["last_treated"] == 0
            else game_data["last_treated"]
        )
        await self._mail_user(
            text="Кого вылечить этой ночью?",
            role_key="doctors",
            new_state=UserFsm.DOCTOR_TREATS,
            exclude=exclude,
        )

    async def mail_policeman(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        exclude = game_data["policeman"]
        await self._mail_user(
            text="Кого проверить этой ночью?",
            role_key="policeman",
            new_state=UserFsm.POLICEMAN_CHECKS,
            exclude=exclude,
        )

    async def send_request_to_vote(
        self,
        game_data: GameCache,
        user_id: int,
        players_ids: LivePlayersIds,
        players: UsersInGame,
    ):
        sent_message = await self.bot.send_message(
            chat_id=user_id,
            text="Проголосуй за того, кто не нравится!",
            reply_markup=send_selection_to_players_kb(
                players_ids=players_ids,
                players=players,
                exclude=user_id,
                user_index_cb=UserVoteIndexCbData,
            ),
        )
        game_data["to_delete"].append(
            [user_id, sent_message.message_id]
        )

    async def suggest_vote(self):
        await self.bot.send_photo(
            chat_id=self.group_chat_id,
            photo="https://studychinese.ru/content/dictionary/pictures/25/12774.jpg",
            caption="Кого обвиним во всем и повесим?",
            reply_markup=participate_in_social_life(),
        )
        game_data: GameCache = await self.state.get_data()
        live_players = game_data["players_ids"]
        players = game_data["players"]
        await asyncio.gather(
            *(
                self.send_request_to_vote(
                    game_data=game_data,
                    user_id=user_id,
                    players_ids=live_players,
                    players=players,
                )
                for user_id in live_players
                if user_id not in game_data["cant_vote"]
            )
        )
