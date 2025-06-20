import asyncio
from abc import ABC
from collections import defaultdict
from collections.abc import Awaitable, Callable
from operator import attrgetter
from typing import TYPE_CHECKING, Concatenate

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from cache.cache_types import (
    GameCache,
    LastInteraction,
    PlayersIds,
    UserGameCache,
    UserIdInt,
)
from general.exceptions import GameIsOver
from general.groupings import Groupings
from general.text import NUMBER_OF_DAY, NUMBER_OF_NIGHT
from keyboards.inline.keypads.to_bot import (
    get_to_bot_kb,
    participate_in_social_life,
)
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from mafia.roles import Killer, Mafia
from mafia.roles.base import (
    ActiveRoleAtNightABC,
    AliasRoleABC,
    RoleABC,
)
from mafia.roles.base.mixins import (
    FinisherOfNight,
    ObligatoryKillerABC,
    ProcedureAfterNightABC,
    ProcedureAfterVotingABC,
)
from states.game import UserFsm
from utils.common import (
    add_message_to_delete,
    get_the_most_frequently_encountered_id,
)
from utils.informing import (
    get_live_players,
    get_profiles,
    get_results_of_goal_identification,
    get_results_of_voting,
    send_messages_after_night,
    send_request_to_vote,
)
from utils.pretty_text import (
    make_build,
)
from utils.state import (
    get_state_and_assign,
    lock_state,
    reset_user_state,
)
from utils.tg import resending_message, unban_users

if TYPE_CHECKING:
    from mafia.pipeline_game import Game


def check_end_of_game[R, **P](
    async_func: Callable[Concatenate["Game", P], Awaitable[R]],
):
    async def wrapper(
        self: "Game", *args: P.args, **kwargs: P.kwargs
    ) -> R:
        result = await async_func(self, *args, **kwargs)
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
        if criminals_count >= players_count - criminals_count:
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
        self.aim_id: UserIdInt | None = None
        self.original_roles_in_fog_of_war: str | None = None
        self.waiting_for_action_at_night = []
        self.waiting_for_action_at_day = []

    async def start_new_night(self):
        game_data: GameCache = await self.state.get_data()
        game_data["number_of_night"] += 1
        game_data["at_night"] = True
        await self.state.set_data(game_data)
        if (
            game_data["number_of_night"] == 1
            and game_data["settings"]["show_roles_after_death"]
            is False
        ):
            players, roles = get_live_players(
                game_data=game_data, all_roles=self.all_roles
            )
            self.original_roles_in_fog_of_war = roles
        else:
            players, _ = get_live_players(
                game_data=game_data,
                all_roles=self.original_roles_in_fog_of_war
                or self.all_roles,
            )
        night_starts_text = make_build(
            f"🌃Наступает ночь {game_data['number_of_night']}"
        )
        await resending_message(
            bot=self.bot,
            chat_id=self.group_chat_id,
            text=f"{night_starts_text}\n\n{players}",
            photo="https://i.pinimg.com/originals/f0/43/ed/f043edcac9690fdec845925508006459.jpg",
            reply_markup=get_to_bot_kb("Действовать!"),
        )

    async def start_discussions(self, game_data: GameCache):
        players_after_night, _ = get_live_players(
            game_data=game_data,
            all_roles=self.original_roles_in_fog_of_war
            or self.all_roles,
        )
        game_data["at_night"] = False
        await self.state.set_data(game_data)
        await resending_message(
            bot=self.bot,
            chat_id=self.group_chat_id,
            text=f"{make_build('💬Пришло время провести следственные мероприятия жителям города!')}\n\n",
            photo="https://i.pinimg.com/originals/b1/80/98/b18098074864e4b1bf5cc8412ced6421.jpg",
            reply_markup=get_to_bot_kb("Пища для размышлений тут"),
        )

    async def send_delay_messages(
        self, game_data: GameCache, at_night: bool
    ):
        if at_night is True:
            unanswered_users = game_data[
                "waiting_for_action_at_night"
            ]
            message = (
                NUMBER_OF_NIGHT.format(game_data["number_of_night"])
                + "😡Ты проспал эту ночь. Бездействие наказывается"
            )
            data = self.waiting_for_action_at_night
        else:
            unanswered_users = game_data["waiting_for_action_at_day"]
            message = (
                NUMBER_OF_DAY.format(game_data["number_of_night"])
                + "😡Голосовать на выборах — обязанность каждого гражданина"
            )
            data = self.waiting_for_action_at_day

        tasks = []
        for user_id in unanswered_users:
            if data.count(user_id) > 0:
                text = (
                    "❗️После этого дня ты выбываешь из игры, если она не завершится раньше. "
                    "Воспользуйся этим шансом по максимуму"
                )
            else:
                if at_night is True:
                    text = "❗️Допустимо проспать только одну ночь"
                else:
                    text = "❗️Допустимо прогулять выборы только один раз"
            tasks.append(
                self.bot.send_message(
                    chat_id=user_id,
                    text=make_build(f"{message}\n\n{text}"),
                    protect_content=game_data["settings"][
                        "protect_content"
                    ],
                )
            )
        await asyncio.gather(*tasks, return_exceptions=True)

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
            if isinstance(current_role, FinisherOfNight):
                tasks.append(
                    current_role.end_night(game_data=game_data)
                )
        await asyncio.gather(*tasks, return_exceptions=True)
        await unban_users(
            bot=self.bot,
            chat_id=game_data["game_chat"],
            users=game_data["cant_talk"],
        )
        game_data["pros"].clear()
        game_data["cons"].clear()
        game_data["vote_for"].clear()
        game_data["refused_to_vote"].clear()
        game_data["messages_after_night"].clear()
        game_data["cant_talk"].clear()
        game_data["cant_vote"].clear()
        game_data["waiting_for_action_at_night"].clear()
        game_data["waiting_for_action_at_day"].clear()
        await self.state.set_data(game_data)

    def _get_roles_if_isinstance[P: ABC](
        self, parent: type[P]
    ) -> list[P]:
        return [
            self.all_roles[role]
            for role in self.all_roles
            if isinstance(self.all_roles[role], parent)
            and self.all_roles[role].is_alias is False
        ]

    @check_end_of_game
    async def sum_up_after_voting(
        self,
    ):
        game_data: GameCache = await self.state.get_data()
        pros = game_data["pros"]
        cons = game_data["cons"]
        removed_user_id = self.aim_id
        result_text = get_results_of_voting(
            game_data=game_data, removed_user_id=removed_user_id
        )
        voting_roles = self._get_roles_if_isinstance(
            parent=ProcedureAfterVotingABC
        )
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
            await asyncio.sleep(1)
            await resending_message(
                bot=self.bot,
                chat_id=self.group_chat_id,
                text=result_text,
            )
            return

        if is_not_there_removed:
            result_text += make_build(
                f"🥳🥳🥳{game_data['players'][str(removed_user_id)]['url']} дали еще шанс!"
            )
            await resending_message(
                bot=self.bot,
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
        await asyncio.sleep(2)
        role = (
            user_info["pretty_role"]
            if game_data["settings"]["show_roles_after_death"]
            else "???"
        )

        other_tasks, boss_is_dead_tasks = self.remove_user_from_game(
            game_data=game_data,
            user_id=removed_user_id,
            at_night=False,
        )
        await self.state.set_data(game_data)
        await resending_message(
            bot=self.bot,
            chat_id=self.group_chat_id,
            text=result_text
            + make_build(
                f"❗️❗️❗️Сегодня народ принял тяжелое решение и повесил "
                f'{user_info["url"]} с ролью {role}!'
            ),
        )
        await asyncio.gather(*other_tasks, return_exceptions=True)
        await asyncio.gather(
            *boss_is_dead_tasks, return_exceptions=True
        )
        await self.state.set_data(game_data)

    @check_end_of_game
    async def sum_up_after_night(self):
        game_data: GameCache = await self.state.get_data()
        roles = self._get_roles_if_isinstance(
            parent=ProcedureAfterNightABC
        )
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

        active_roles = self._get_roles_if_isinstance(
            parent=ActiveRoleAtNightABC
        )
        for active_role in active_roles:
            active_role.leave_notification_message(
                game_data=game_data
            )
        text_about_dead = ""
        other_tasks = []
        boss_is_dead_tasks = []
        for victim_id in victims:
            other, boss_is_dead = self.remove_user_from_game(
                game_data=game_data,
                user_id=victim_id,
                at_night=True,
            )
            other_tasks.extend(other)
            boss_is_dead_tasks.extend(boss_is_dead)
            url = game_data["players"][str(victim_id)]["url"]
            role = (
                game_data["players"][str(victim_id)]["pretty_role"]
                if game_data["settings"]["show_roles_after_death"]
                else "???"
            )
            killer = (
                killers_of[victim_id][0].pretty_role
                if game_data["settings"]["show_killers"]
                else "???"
            )
            text_about_dead += (
                f"🌹Убит {role} — {url}.\n\n"
                f"Один из виновных — {killer}!\n{"━" * 18}\n\n"
            )
        text_about_dead = (
            text_about_dead or "💕Сегодня ночью все выжили!"
        )
        await self.state.set_data(game_data)
        await resending_message(
            bot=self.bot,
            chat_id=self.group_chat_id,
            text=make_build(text_about_dead),
        )
        await send_messages_after_night(
            game_data=game_data,
            bot=self.bot,
            group_chat_id=self.group_chat_id,
        )
        await asyncio.gather(*other_tasks, return_exceptions=True)
        await asyncio.gather(
            *boss_is_dead_tasks, return_exceptions=True
        )
        await self.state.set_data(game_data)
        await asyncio.sleep(3)
        return game_data

    async def confirm_final_aim(
        self,
    ) -> bool:
        game_data: GameCache = await self.state.get_data()
        vote_for = game_data["vote_for"]
        text = get_results_of_goal_identification(
            game_data=game_data
        )
        self.aim_id = get_the_most_frequently_encountered_id(
            [voted for _, voted in vote_for],
            counterweight=len(game_data["refused_to_vote"]),
        )
        await self.state.set_data(game_data)
        await resending_message(
            bot=self.bot, chat_id=self.group_chat_id, text=text
        )
        if self.aim_id is None:
            return False
        await asyncio.sleep(2)
        url = game_data["players"][str(self.aim_id)]["url"]
        sent_survey = await resending_message(
            bot=self.bot,
            chat_id=self.group_chat_id,
            text=make_build(f"На кону судьба {url}!"),
            reply_markup=get_vote_for_aim_kb(
                user_id=self.aim_id,
                pros=game_data["pros"],
                cons=game_data["cons"],
            ),
        )
        await sent_survey.pin()
        add_message_to_delete(
            game_data=game_data,
            chat_id=self.group_chat_id,
            message_id=sent_survey.message_id,
        )
        await self.state.set_data(game_data)
        return True

    def remove_user_from_game(
        self,
        game_data: GameCache,
        user_id: int,
        at_night: bool | None,
        message_if_died_especially: str | None = None,
    ):
        user_role = game_data["players"][str(user_id)]["role_id"]
        role: RoleABC = self.all_roles[user_role]
        boss_is_dead_tasks = []
        other_tasks = []
        if at_night is True or (
            at_night is None
            and message_if_died_especially is not None
        ):
            other_tasks.append(
                get_state_and_assign(
                    dispatcher=self.dispatcher,
                    chat_id=user_id,
                    bot_id=self.bot.id,
                    new_state=UserFsm.WAIT_FOR_LATEST_LETTER,
                )
            )
        elif at_night is None or (
            at_night is False and role.clearing_state_after_death
        ):
            other_tasks.append(
                reset_user_state(
                    dispatcher=self.dispatcher,
                    user_id=user_id,
                    bot_id=self.bot.id,
                )
            )

        game_data["live_players_ids"].remove(user_id)
        game_data["players"][str(user_id)][
            "number_died_at_night"
        ] = (game_data["number_of_night"] - 1)
        game_data[role.roles_key].remove(user_id)
        other_tasks.append(
            role.report_death(
                game_data=game_data,
                at_night=at_night,
                user_id=user_id,
                message_if_died_especially=message_if_died_especially,
            )
        )
        if role.alias:
            boss_is_dead_tasks.append(
                role.boss_is_dead(
                    current_id=user_id, game_data=game_data
                )
            )
        if isinstance(role, AliasRoleABC):
            other_tasks.append(
                role.alias_is_dead(
                    current_id=user_id, game_data=game_data
                )
            )
        return other_tasks, boss_is_dead_tasks

    async def mailing(self):
        async with lock_state(self.state):
            game_data: GameCache = await self.state.get_data()
            active_roles = self._get_roles_if_isinstance(
                ActiveRoleAtNightABC
            )
            await asyncio.gather(
                *(
                    role.mailing(game_data=game_data)
                    for role in active_roles
                ),
                return_exceptions=True,
            )
            await self.state.set_data(game_data)
        return game_data

    async def suggest_vote(self):
        await resending_message(
            bot=self.bot,
            chat_id=self.group_chat_id,
            text="Кого обвиним во всем и повесим?",
            photo="https://studychinese.ru/content/dictionary/pictures/25/12774.jpg",
            reply_markup=participate_in_social_life(),
        )
        async with lock_state(self.state):
            game_data: GameCache = await self.state.get_data()
            live_players_ids = game_data["live_players_ids"]
            await asyncio.gather(
                *(
                    send_request_to_vote(
                        game_data=game_data,
                        user_id=user_id,
                        players_ids=live_players_ids,
                        players=game_data["players"],
                        bot=self.bot,
                    )
                    for user_id in live_players_ids
                    if user_id not in game_data["cant_vote"]
                ),
                return_exceptions=True,
            )
            await self.state.set_data(game_data)

    @staticmethod
    def _add_user_to_deleted(
        waiting_for: PlayersIds,
        live_players_ids: PlayersIds,
        inactive_users: PlayersIds,
    ):
        potentially_deleted = set()
        for user_id in waiting_for:
            if user_id not in live_players_ids:
                continue
            if (
                user_id in potentially_deleted
                and user_id not in inactive_users
            ):
                inactive_users.append(user_id)
            else:
                potentially_deleted.add(user_id)

    @check_end_of_game
    async def removing_players(self):
        game_data: GameCache = await self.state.get_data()
        removed_users = []
        self.waiting_for_action_at_night.extend(
            game_data["waiting_for_action_at_night"]
        )
        self.waiting_for_action_at_day.extend(
            game_data["waiting_for_action_at_day"]
        )
        self._add_user_to_deleted(
            waiting_for=self.waiting_for_action_at_night,
            live_players_ids=game_data["live_players_ids"],
            inactive_users=removed_users,
        )
        self._add_user_to_deleted(
            waiting_for=self.waiting_for_action_at_day,
            live_players_ids=game_data["live_players_ids"],
            inactive_users=removed_users,
        )
        other_tasks = []
        boss_is_dead_tasks = []
        for user_id in removed_users:
            other, boss_is_dead = self.remove_user_from_game(
                game_data=game_data,
                user_id=user_id,
                at_night=None,
            )
            other_tasks.extend(other)
            boss_is_dead_tasks.extend(boss_is_dead)

        current_inactive_users = removed_users[:]
        obligatory_killers = self._get_roles_if_isinstance(
            ObligatoryKillerABC
        )
        for killer in obligatory_killers:
            result = killer.kill_after_all_actions(
                game_data=game_data,
                current_inactive_users=current_inactive_users,
            )
            if result is None:
                continue
            user_id, message_to_user = result
            if user_id in removed_users:
                continue
            removed_users.append(user_id)
            other, boss_is_dead = self.remove_user_from_game(
                game_data=game_data,
                user_id=user_id,
                at_night=None,
                message_if_died_especially=message_to_user,
            )
            other_tasks.extend(other)
            boss_is_dead_tasks.extend(boss_is_dead)
        if not removed_users:
            return
        await self.state.set_data(game_data)
        profiles = get_profiles(
            players_ids=removed_users,
            players=game_data["players"],
            show_current_roles=game_data["settings"][
                "show_roles_after_death"
            ],
        )
        text = f"{make_build('❗️Игроки выбывают:')}\n{profiles}"
        await resending_message(
            bot=self.bot,
            chat_id=self.group_chat_id,
            text=text,
            photo="https://media.zenfs.com/en/nerdist_761/342f5f2b17659cb424aaabef1951a1a1",
        )
        await asyncio.gather(*other_tasks, return_exceptions=True)
        await asyncio.gather(
            *boss_is_dead_tasks, return_exceptions=True
        )
        await self.state.set_data(game_data)
        self.waiting_for_action_at_night = list(
            user_id
            for user_id in self.waiting_for_action_at_night
            if user_id in game_data["live_players_ids"]
        )
        self.waiting_for_action_at_day = list(
            user_id
            for user_id in self.waiting_for_action_at_day
            if user_id in game_data["live_players_ids"]
        )
