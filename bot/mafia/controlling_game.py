import asyncio
from collections import defaultdict
from collections.abc import Callable
from operator import attrgetter
from typing import TYPE_CHECKING

from aiogram import Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from loguru import logger

from cache.cache_types import (
    GameCache,
    UserGameCache,
    LastInteraction,
)
from general.collection_of_roles import get_data_with_roles
from general.exceptions import GameIsOver
from general.groupings import Groupings

from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from states.states import UserFsm
from utils.pretty_text import (
    make_pretty,
    make_build,
)
from utils.common import get_the_most_frequently_encountered_id
from utils.informing import (
    get_profiles,
    get_results_of_goal_identification,
    get_results_of_voting,
    send_messages_after_night,
    send_request_to_vote,
)
from utils.state import get_state_and_assign, reset_user_state

from mafia.roles import Mafia, Killer, Prosecutor, Forger, Traitor
from mafia.roles.base import (
    AliasRoleABC,
    RoleABC,
    ActiveRoleAtNightABC,
)
from mafia.roles.base.mixins import (
    ProcedureAfterNightABC,
    FinalNightABC,
    ProcedureAfterVotingABC,
)

if TYPE_CHECKING:
    from mafia.pipeline_game import Game


def check_end_of_game(async_func: Callable):
    async def wrapper(self: "Game"):
        result = await async_func(self)
        state = self.state
        game_data: GameCache = await state.get_data()
        players_count = len(game_data["live_players_ids"])
        if not game_data[Mafia.roles_key]:
            if not game_data.get(Killer.roles_key):
                raise GameIsOver(winner=Groupings.civilians)
            killers_count = len(game_data.get(Killer.roles_key))
            if killers_count >= players_count - killers_count:
                raise GameIsOver(winner=Groupings.killer)
        criminals_count = 0
        for role in self.all_roles:
            current_role: RoleABC = self.all_roles[role]
            if current_role.grouping == Groupings.criminals:
                if current_role.is_alias:
                    continue
                criminals_count += len(
                    game_data[current_role.roles_key]
                )
        if (
            # criminals_count
            # >= players_count - criminals_count
            criminals_count
            == players_count
        ):  # TODO >=
            raise GameIsOver(winner=Groupings.criminals)
        return result

    return wrapper


class Controller:
    def __init__(
        self,
        bot: Bot,
        group_chat_id: int,
        state: FSMContext,
        dispatcher: Dispatcher,
    ):

        self.state = state
        self.dispatcher = dispatcher
        self.bot = bot
        self.group_chat_id = group_chat_id
        self.all_roles = {}

    async def end_night(self):
        game_data: GameCache = await self.state.get_data()
        tasks = []
        for role in self.all_roles:
            current_role: RoleABC = self.all_roles[role]
            if (
                current_role.alias
                and current_role.alias.is_mass_mailing_list
                and current_role.last_interactive_key
            ):
                current_night = game_data["number_of_night"]
                processed_user_id = (
                    current_role.get_processed_user_id(game_data)
                )
                if processed_user_id:
                    last_interactive: LastInteraction = game_data[
                        current_role.last_interactive_key
                    ]
                    excess_players = [
                        user_id_str
                        for user_id_str, nights in last_interactive.items()
                        if nights
                        and nights[-1] == current_night
                        and str(processed_user_id) != user_id_str
                    ]
                    for user_id_str in excess_players:
                        last_interactive[user_id_str].pop()

            if current_role.processed_users_key in game_data:
                game_data[current_role.processed_users_key].clear()
            if current_role.processed_by_boss:
                game_data[current_role.processed_by_boss].clear()
            if current_role.extra_data:
                for extra in current_role.extra_data:
                    if (
                        extra.need_to_clear
                        and extra.key in game_data
                    ):
                        game_data[extra.key].clear()
            if isinstance(current_role, FinalNightABC):
                tasks.append(
                    current_role.end_night(game_data=game_data)
                )
        await asyncio.gather(*tasks, return_exceptions=True)
        game_data["pros"].clear()
        game_data["cons"].clear()
        game_data["vote_for"].clear()
        game_data["messages_after_night"].clear()
        await self.state.set_data(game_data)

    def get_voting_roles(self):
        return [
            self.all_roles[role]
            for role in self.all_roles
            if isinstance(
                self.all_roles[role], ProcedureAfterVotingABC
            )
            and self.all_roles[role].is_alias is False
        ]

    @check_end_of_game
    async def sum_up_after_voting(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        pros = game_data["pros"]
        cons = game_data["cons"]
        removed_user_id = get_the_most_frequently_encountered_id(
            [voted for _, voted in game_data["vote_for"]]
        )
        result_text = get_results_of_voting(
            game_data=game_data, removed_user_id=removed_user_id
        )
        voting_roles = self.get_voting_roles()
        voting_roles.sort(
            key=attrgetter("number_in_order_after_voting")
        )
        is_not_there_removed = len(pros) == len(cons) or len(
            pros
        ) < len(cons)
        kwargs = {
            "game_data": game_data,
            "is_not_there_removed": is_not_there_removed,
            "initial_removed_user_id": removed_user_id,
        }
        if is_not_there_removed:
            removed_user = [0]
        else:
            removed_user = [removed_user_id]
        for role in voting_roles:
            await role.take_action_after_voting(
                **kwargs,
                removed_user=removed_user,
            )
        await self.state.set_data(game_data)
        if removed_user_id is None:
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text=result_text,
            )
            return

        if is_not_there_removed:
            result_text += make_build(
                f"🥳🥳🥳{game_data['players'][str(removed_user_id)]['url']} дали еще шанс!"
            )
            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text=result_text,
            )
            return
        if removed_user_id != removed_user[0]:
            return
        user_info: UserGameCache = game_data["players"][
            str(removed_user_id)
        ]
        for user_id in set(pros):
            current_role = self.all_roles[
                game_data["players"][str(user_id)]["role_id"]
            ]
            current_role.earn_money_for_voting(
                voted_role=self.all_roles[user_info["role_id"]],
                voted_user=user_info,
                game_data=game_data,
                user_id=user_id,
            )
        await self.remove_user_from_game(
            game_data=game_data,
            user_id=removed_user_id,
            at_night=False,
        )
        await self.bot.send_message(
            chat_id=self.group_chat_id,
            text=result_text
            + make_build(
                f"❗️❗️❗️Сегодня народ принял тяжелое решение и повесил "
                f'{user_info["url"]} с ролью {user_info["pretty_role"]}!'
            ),
        )
        await self.state.set_data(game_data)

    @check_end_of_game
    async def sum_up_after_night(self):
        game_data: GameCache = await self.state.get_data()
        roles: list[ProcedureAfterNightABC] = [
            self.all_roles[role]
            for role in self.all_roles
            if isinstance(
                self.all_roles[role], ProcedureAfterNightABC
            )
            and self.all_roles[role].is_alias is False
        ]
        roles.sort(key=attrgetter("number_in_order_after_night"))
        victims = set()
        recovered = []
        murdered = []
        killers_of = defaultdict(list)
        kwargs = {
            "recovered": recovered,
            "murdered": murdered,
            "victims": victims,
            "game_data": game_data,
            "killers_of": killers_of,
        }
        for role in roles:
            await role.procedure_after_night(**kwargs)
        victims |= set(murdered) - set(recovered)
        for role in roles:
            await role.accrual_of_overnight_rewards(**kwargs)
        text_about_dead = ""
        tasks = []
        for victim_id in victims:
            tasks.append(
                self.remove_user_from_game(
                    game_data=game_data,
                    user_id=victim_id,
                    at_night=True,
                )
            )
            url = game_data["players"][str(victim_id)]["url"]
            role = game_data["players"][str(victim_id)][
                "pretty_role"
            ]
            text_about_dead += f"🌹Убит {role} - {url}!\n\n"
        text_about_dead = (
            text_about_dead or "💕Сегодня ночью все выжили!"
        )
        await self.bot.send_message(
            chat_id=self.group_chat_id,
            text=make_build(text_about_dead),
        )
        await send_messages_after_night(
            game_data=game_data,
            bot=self.bot,
            group_chat_id=self.group_chat_id,
        )
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.state.set_data(game_data)
        return game_data

    async def confirm_final_aim(
        self,
    ) -> bool:
        game_data: GameCache = await self.state.get_data()
        vote_for = game_data["vote_for"]
        aim_id = get_the_most_frequently_encountered_id(
            [voted for _, voted in vote_for]
        )
        text = get_results_of_goal_identification(
            game_data=game_data
        )
        await self.state.set_data(game_data)
        await self.bot.send_message(
            chat_id=self.group_chat_id,
            text=text,
        )
        if aim_id is None:
            return False
        url = game_data["players"][str(aim_id)]["url"]
        sent_survey = await self.bot.send_message(
            chat_id=self.group_chat_id,
            text=make_build(f"На кону судьба {url}!"),
            reply_markup=get_vote_for_aim_kb(
                user_id=aim_id,
                pros=game_data["pros"],
                cons=game_data["cons"],
            ),
        )
        await sent_survey.pin()
        game_data["to_delete"].append(
            [self.group_chat_id, sent_survey.message_id]
        )
        await self.state.set_data(game_data)
        return True

    async def remove_user_from_game(
        self,
        game_data: GameCache,
        user_id: int,
        at_night: bool | None,
    ):
        user_role = game_data["players"][str(user_id)]["role_id"]
        role: RoleABC = self.all_roles[user_role]
        if at_night is True:
            await get_state_and_assign(
                dispatcher=self.dispatcher,
                chat_id=user_id,
                bot_id=self.bot.id,
                new_state=UserFsm.WAIT_FOR_LATEST_LETTER,
            )
        elif at_night is None or (
            at_night is False and role.clearing_state_after_death
        ):
            await reset_user_state(
                dispatcher=self.dispatcher,
                user_id=user_id,
                bot_id=self.bot.id,
            )
        game_data["live_players_ids"].remove(user_id)
        game_data["players"][str(user_id)][
            "number_died_at_night"
        ] = (game_data["number_of_night"] - 1)
        game_data[role.roles_key].remove(user_id)
        try:
            await role.report_death(
                game_data=game_data,
                at_night=at_night,
                user_id=user_id,
            )
        except Exception as e:
            logger.exception("Error")
        if role.alias:
            await role.boss_is_dead(
                current_id=user_id, game_data=game_data
            )
        if isinstance(role, AliasRoleABC):
            await role.alias_is_dead(
                current_id=user_id, game_data=game_data
            )

    async def mailing(self):
        game_data: GameCache = await self.state.get_data()
        tasks = []
        for role in self.all_roles:
            current_role: RoleABC = self.all_roles[role]
            if (
                isinstance(current_role, ActiveRoleAtNightABC)
                is False
                or current_role.is_alias
            ):
                continue
            tasks.append(current_role.mailing(game_data=game_data))
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.state.set_data(game_data)

    async def suggest_vote(self):
        message = await self.bot.send_photo(
            chat_id=self.group_chat_id,
            photo="https://studychinese.ru/content/dictionary/pictures/25/12774.jpg",
            caption="Кого обвиним во всем и повесим?",
            reply_markup=participate_in_social_life(),
        )
        await message.pin()
        game_data: GameCache = await self.state.get_data()
        live_players = game_data["live_players_ids"]
        players = game_data["players"]
        banned_user = Prosecutor().get_processed_user_id(game_data)
        await asyncio.gather(
            *(
                send_request_to_vote(
                    game_data=game_data,
                    user_id=user_id,
                    players_ids=live_players,
                    players=players,
                    bot=self.bot,
                )
                for user_id in live_players
                if user_id != banned_user
            ),
            return_exceptions=True,
        )
        await self.state.set_data(game_data)

    @check_end_of_game
    async def removing_inactive_players(self):
        return
        game_data: GameCache = await self.state.get_data()
        wait_for = game_data["wait_for"]
        potentially_deleted = set()
        inactive_users = []
        for user_id in wait_for:
            if user_id not in game_data["live_players_ids"]:
                continue
            if user_id in potentially_deleted:
                inactive_users.append(user_id)
            else:
                potentially_deleted.add(user_id)
        if not inactive_users:
            return
        wait_for[:] = list(
            user_id
            for user_id in set(wait_for) - set(inactive_users)
            if user_id in game_data["live_players_ids"]
        )
        profiles = get_profiles(
            players_ids=inactive_users,
            players=game_data["players"],
            role=True,
        )
        text = f"{make_build('❗️Игроки выбывают:')}\n{profiles}"
        await self.bot.send_photo(
            chat_id=self.group_chat_id,
            photo="https://media.zenfs.com/en/nerdist_761/342f5f2b17659cb424aaabef1951a1a1",
            caption=text,
        )
        await asyncio.gather(
            *(
                self.remove_user_from_game(
                    game_data=game_data,
                    user_id=user_id,
                    at_night=None,
                )
                for user_id in inactive_users
            ),
            return_exceptions=True,
        )
        await self.state.set_data(game_data)

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
                    chat_id=persons[0],
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
            ),
            return_exceptions=True,
        )
