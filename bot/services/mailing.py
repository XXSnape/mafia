import asyncio
from itertools import groupby
from operator import itemgetter

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from cache.cache_types import (
    GameCache,
    LivePlayersIds,
    UserGameCache,
    UsersInGame,
)
from constants.output import NUMBER_OF_NIGHT
from general.collection_of_roles import Roles
from keyboards.inline.callback_factory.recognize_user import (
    UserVoteIndexCbData,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from services.roles import Prosecutor
from services.roles.base import ActiveRoleAtNight, Role
from utils.utils import (
    get_profiles,
    get_state_and_assign,
    make_pretty,
    make_build,
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
        self.all_roles = {}

    async def mailing(self):
        game_data: GameCache = await self.state.get_data()
        for role in self.all_roles:
            current_role: Role = self.all_roles[role]
            if isinstance(current_role, ActiveRoleAtNight) is False:
                continue
            await current_role.mailing(game_data=game_data)

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
        banned_user = Prosecutor().get_processed_user_id(game_data)
        await asyncio.gather(
            *(
                self.send_request_to_vote(
                    game_data=game_data,
                    user_id=user_id,
                    players_ids=live_players,
                    players=players,
                )
                for user_id in live_players
                if user_id != banned_user
            )
        )

    async def send_messages_after_night(self, game_data: GameCache):
        messages = game_data["messages_after_night"]
        if messages:
            group_iter = groupby(messages, key=itemgetter(0))
            number_of_night = make_build(
                f"События ночи {game_data['number_of_night']}:\n\n"
            )
            await asyncio.gather(
                *(
                    self.bot.send_message(
                        chat_id=user_id,
                        text=number_of_night
                        + "\n\n".join(
                            f"{number}) {message[1]}"
                            for number, message in enumerate(
                                messages, start=1
                            )
                        ),
                    )
                    for user_id, messages in group_iter
                )
            )

    async def familiarize_players(self, game_data: GameCache):
        for user_id, player_data in game_data["players"].items():
            player_data: UserGameCache
            current_role = Roles[player_data["enum_name"]].value
            if current_role.is_alias:
                continue
            roles = game_data[current_role.roles_key]
            await self.bot.send_photo(
                chat_id=roles[0],
                photo=current_role.photo,
                caption=f"Твоя роль - "
                f"{make_pretty(current_role.role)}! "
                f"{current_role.purpose}",
            )
            if current_role.alias and len(roles) > 1:
                profiles = get_profiles(
                    live_players_ids=roles,
                    players=game_data["players"],
                    role=True,
                )
                await self.bot.send_message(
                    chat_id=roles[0],
                    text="Твои союзники!\n\n" + profiles,
                )
                for user_id in roles[1:]:
                    await self.bot.send_photo(
                        chat_id=user_id,
                        photo=current_role.alias.photo,
                        caption=f"Твоя роль - "
                        f"{make_pretty(current_role.alias.role)}!"
                        f" {current_role.alias.purpose}",
                    )
                    await self.bot.send_message(
                        chat_id=user_id,
                        text="Твои союзники!\n\n" + profiles,
                    )
                    if (
                        current_role.alias.state_for_waiting_for_action
                    ):
                        await get_state_and_assign(
                            dispatcher=self.dispatcher,
                            chat_id=user_id,
                            bot_id=self.bot.id,
                            new_state=current_role.alias.state_for_waiting_for_action,
                        )
