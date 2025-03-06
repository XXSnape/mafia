import asyncio
from collections.abc import Iterable
from pprint import pprint
from typing import Literal

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from telebot.types import InlineKeyboardMarkup

from cache.cache_types import (
    GameCache,
    RolesKeysLiteral,
    LivePlayersIds,
    UsersInGame,
    Roles,
    Role,
    PlayersIds,
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
from utils.utils import (
    make_pretty,
    get_state_and_assign,
    get_profiles,
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

    @staticmethod
    def generate_markup(
        player_id: int,
        current_role: Role,
        game_data: GameCache,
    ):
        exclude = []
        current_number = game_data["number_of_night"]
        if current_role.interactive_with.is_self_selecting is False:
            exclude = [player_id]
        for processed_user_id, number in game_data.get(
            current_role.interactive_with.last_interactive_key, {}
        ).items():
            if int(processed_user_id) == player_id:
                constraint = current_role.interactive_with.self
            else:
                constraint = current_role.interactive_with.other
            if constraint is None:
                exclude.append(int(processed_user_id))
            elif (current_number - number) < constraint + 1:
                exclude.append(int(processed_user_id))
        if game_data["players_ids"] == exclude:
            return
        return send_selection_to_players_kb(
            players_ids=game_data["players_ids"],
            players=game_data["players"],
            exclude=exclude,
            extra_buttons=current_role.extra_buttons_for_actions_at_night,
        )

    async def send_survey(
        self,
        player_id: int,
        current_role: Role,
        game_data: GameCache,
    ):
        # exclude = []
        # current_number = game_data["number_of_night"]
        # if current_role.interactive_with.is_self_selecting is False:
        #     exclude = [player_id]
        # for processed_user_id, number in game_data.get(
        #     current_role.interactive_with.last_interactive_key, {}
        # ).items():
        #     if int(processed_user_id) == player_id:
        #         constraint = current_role.interactive_with.self
        #     else:
        #         constraint = current_role.interactive_with.other
        #     if constraint is None:
        #         exclude.append(int(processed_user_id))
        #     elif (current_number - number) < constraint + 1:
        #         exclude.append(int(processed_user_id))
        # if game_data["players_ids"] == exclude:
        #     return

        markup = self.generate_markup(
            player_id=player_id,
            current_role=current_role,
            game_data=game_data,
        )

        # markup = send_selection_to_players_kb(
        #     players_ids=game_data["players_ids"],
        #     players=game_data["players"],
        #     exclude=exclude,
        #     extra_buttons=current_role.extra_buttons_for_actions_at_night,
        # )
        sent_survey = await self.bot.send_message(
            chat_id=player_id,
            text=current_role.interactive_with.mail_message,
            reply_markup=markup,
        )
        await self.save_msg_to_delete_and_change_state(
            game_data=game_data,
            player_id=player_id,
            current_role=current_role,
            message_id=sent_survey.message_id,
        )

    async def save_msg_to_delete_and_change_state(
        self,
        game_data: GameCache,
        player_id: int,
        current_role: Role,
        message_id: int,
    ):
        game_data["to_delete"].append([player_id, message_id])
        await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=player_id,
            bot_id=self.bot.id,
            new_state=current_role.state_for_waiting_for_action,
        )

    async def mailing(self):
        game_data: GameCache = await self.state.get_data()
        pprint(game_data)
        for role in Roles:
            print("hello")
            current_role: Role = role.value
            if (current_role.roles_key not in game_data) or (
                current_role.interactive_with is None
            ):
                print(current_role.roles_key, "not in game data")
                continue
            if (
                current_role.interactive_with.players_to_send_messages
            ):
                roles = current_role.interactive_with.players_to_send_messages(
                    game_data
                )
            else:
                roles = game_data[current_role.roles_key]
                print("roles", roles)
            if not roles:
                continue
            if current_role.interactive_with.own_mailing_markup:
                sent_survey = await self.bot.send_message(
                    chat_id=roles[0],
                    text=current_role.interactive_with.mail_message,
                    reply_markup=current_role.interactive_with.own_mailing_markup,
                )
                await self.save_msg_to_delete_and_change_state(
                    game_data=game_data,
                    player_id=roles[0],
                    current_role=current_role,
                    message_id=sent_survey.message_id,
                )
                continue
            await self.send_survey(
                player_id=roles[0],
                current_role=current_role,
                game_data=game_data,
            )
            if (
                current_role.alias
                and current_role.alias.is_mass_mailing_list
            ):
                current_role = current_role.alias.role.value
                for user_id in roles[1:]:
                    await self.send_survey(
                        player_id=user_id,
                        current_role=current_role,
                        game_data=game_data,
                    )
        print("end mail")

    async def send_info_to_player(
        self, game_data: GameCache, role: Roles, key: str
    ):
        current_role: Role = role.value
        players = game_data.get(current_role.roles_key, [])
        if not players:
            return

        player_id = players[0]
        if not game_data[current_role.processed_users_key]:
            return

        user_id = game_data[current_role.processed_users_key][0]
        visitors = ", ".join(
            game_data["players"][str(user_id)]["url"]
            for user_id in game_data["tracking"]
            .get(str(user_id), {})
            .get(key, [])
        )
        user_url = game_data["players"][str(user_id)]["url"]
        if key == "interacting":
            message = (
                f"{user_url} сегодня никто не навещал"
                if not visitors
                else f"К {user_url} приходили: {visitors}"
            )
        else:
            message = (
                f"{user_url} cегодня ни к кому не ходил"
                if not visitors
                else f"{user_url} навещал: {visitors}"
            )
        await self.bot.send_message(chat_id=player_id, text=message)

    async def send_promised_information_to_users(self):
        game_data: GameCache = await self.state.get_data()
        if game_data["disclosed_roles"]:
            user_id, role = game_data["disclosed_roles"][0]
            if game_data.get("forged_roles"):
                faked_id, faked_role = game_data["forged_roles"][0]
                if faked_id == user_id:
                    role = faked_role
            for policeman_id in game_data["policeman"]:
                url = game_data["players"][str(user_id)]["url"]
                await self.bot.send_message(
                    chat_id=policeman_id, text=f"{url} - {role}!"
                )
        await self.send_info_to_player(
            game_data=game_data,
            role=Roles.journalist,
            key="interacting",
        )
        await self.send_info_to_player(
            game_data=game_data, role=Roles.agent, key="sufferers"
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

    async def report_death(
        self,
        chat_id: int,
        bombers: PlayersIds,
    ):

        await get_state_and_assign(
            dispatcher=self.dispatcher,
            chat_id=chat_id,
            bot_id=self.bot.id,
            new_state=UserFsm.WAIT_FOR_LATEST_LETTER,
        )
        message = "К сожалению, тебя убили! Отправь напоследок все, что думаешь!"
        if chat_id in bombers:
            message = "Поздравляю с заветным ночным убийством! Не забудь поглумиться над мафией"
        await self.bot.send_message(
            chat_id=chat_id,
            text=message,
        )

    async def familiarize_players(self):
        game_data: GameCache = await self.state.get_data()
        for role in Roles:
            current_role: Role = role.value

            roles = game_data.get(current_role.roles_key)
            if not roles:
                continue
            await self.bot.send_photo(
                chat_id=roles[0],
                photo=current_role.photo,
                caption=f"Твоя роль - "
                f"{make_pretty(current_role.role)}! "
                f"{current_role.purpose}",
            )
            if current_role.alias:
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
                        photo=current_role.alias.role.value.photo,
                        caption=f"Твоя роль - "
                        f"{make_pretty(current_role.alias.role.value.role)}!"
                        f" {current_role.alias.role.value.purpose}",
                    )
                    await self.bot.send_message(
                        chat_id=user_id,
                        text="Твои союзники!\n\n" + profiles,
                    )
                    if (
                        current_role.alias.is_mass_mailing_list
                        is False
                    ):
                        await get_state_and_assign(
                            dispatcher=self.dispatcher,
                            chat_id=user_id,
                            bot_id=self.bot.id,
                            new_state=current_role.alias.role.value.state_for_waiting_for_action,
                        )
