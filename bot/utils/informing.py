import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING

from aiogram import Bot

from cache.cache_types import (
    GameCache,
    UserIdInt,
    PlayersIds,
    UsersInGame,
    LivePlayersIds,
)
from constants.output import MONEY_SYM, NUMBER_OF_NIGHT
from general.groupings import Groupings
from keyboards.inline.callback_factory.recognize_user import (
    UserVoteIndexCbData,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)

from utils.pretty_text import make_build, make_pretty

if TYPE_CHECKING:
    from mafia.roles import Role


def get_live_players(
    game_data: GameCache, all_roles: dict[str, "Role"]
):
    profiles = get_profiles(
        players_ids=game_data["live_players_ids"],
        players=game_data["players"],
    )
    live_roles = get_live_roles(
        game_data=game_data, all_roles=all_roles
    )
    return (
        f"{make_build('💗Живые игроки:')}\n"
        f"{profiles}\n\n"
        f"{make_build('Состав группировок:')}\n"
        f"{live_roles}\n\n"
    )


def get_live_roles(
    game_data: GameCache, all_roles: dict[str, "Role"]
):
    gropings: dict[Groupings, list[tuple[str, int]]] = {
        Groupings.civilians: [],
        Groupings.criminals: [],
        Groupings.killer: [],
        Groupings.other: [],
    }
    for role in all_roles:
        current_role = all_roles[role]
        if not game_data[current_role.roles_key]:
            continue
        grouping = gropings[current_role.grouping]
        text = current_role.role
        if current_role.alias:
            count = 1
        elif current_role.is_alias:
            count = len(game_data[current_role.roles_key][1:])
        else:
            count = len(game_data[current_role.roles_key])
        if count == 0:
            continue
        if count > 1:
            count_text = f" ({count})"
            text += make_build(count_text)
        grouping.append((text, count))
    result = ""
    for grouping, roles in gropings.items():
        if not roles:
            continue
        grouping_roles = "\n● ".join(role for role, _ in roles)
        total = sum(count for _, count in roles)
        total_text = make_build(f"- {total}:")
        result += f"\n{grouping.value.name} {total_text}\n● {grouping_roles}\n"
    return result


def get_profiles(
    players_ids: PlayersIds,
    players: UsersInGame,
    role: bool = False,
    initial_role: bool = False,
    money_need: bool = False,
) -> str:
    result = ""
    if not players_ids:
        return "Пока нет участников!"

    for (
        index,
        user_id,
    ) in enumerate(players_ids, start=1):
        url = players[str(user_id)]["url"]
        if role:
            if initial_role:
                role = players[str(user_id)]["initial_role"]
            else:
                role = players[str(user_id)]["pretty_role"]
            if money_need:
                money = players[str(user_id)]["money"]
                result += (
                    f"\n{index}) {url} - {role} ({money}{MONEY_SYM})"
                )
            else:
                result += f"\n{index}) {url} - {role}"
        else:
            result += f"\n{index}) {url}"
    return result


def get_profiles_during_registration(
    live_players_ids: LivePlayersIds, players: UsersInGame
) -> str:
    profiles = get_profiles(live_players_ids, players)
    return make_build(
        f"Скорее присоединяйся к игре!\nУчастники:\n{profiles}"
    )


def get_results_of_goal_identification(game_data: GameCache):
    def sorting_by_voting(voting_data):
        return len(voting_data[1])

    result = make_build(
        f"❗️Результаты голосования дня {game_data['number_of_night']}:"
    )

    vote_for = game_data["vote_for"]
    voting = defaultdict(list)
    for voting_id, voted_id in vote_for:
        voting[game_data["players"][str(voted_id)]["url"]].append(
            game_data["players"][str(voting_id)]["url"]
        )

    result_voting = ""
    if not voting:
        result_voting = make_build(
            "\n\n😯Сегодня нет потенциальных жертв!"
        )
        return result + result_voting
    for voted, voting_people in sorted(
        voting.items(), key=sorting_by_voting, reverse=True
    ):
        result_voting += (
            f"\n\n📝Голосовавшие за {voted} ({len(voting_people)}):\n● "
            + "\n● ".join(
                voting_person for voting_person in voting_people
            )
        )
    return result + result_voting


def get_results_of_voting(
    game_data: GameCache, removed_user_id: UserIdInt
):
    if not removed_user_id:
        return make_build(
            "Доброта или банальная несогласованность? Посмотрим, воспользуются ли преступники таким подарком."
        )

    user_url = game_data["players"][str(removed_user_id)]["url"]
    pros = len(game_data["pros"])
    cons = len(game_data["cons"])
    return (
        make_build(f"Подводим итоги судьбы {user_url}:\n\n")
        + f"✅За линчевание - {pros}\n🚫Против - {cons}\n\n"
    )


async def notify_aliases_about_transformation(
    game_data: GameCache,
    bot: Bot,
    new_role: "Role",
    user_id: int,
):
    url = game_data["players"][str(user_id)]["url"]
    initial_role = game_data["players"][str(user_id)]["initial_role"]
    profiles = get_profiles(
        players_ids=game_data[new_role.roles_key],
        players=game_data["players"],
        role=True,
    )
    await asyncio.gather(
        *(
            bot.send_photo(
                chat_id=player_id,
                photo=new_role.photo,
                caption=NUMBER_OF_NIGHT.format(
                    game_data["number_of_night"]
                )
                + f"{initial_role} {url} превратился в {make_pretty(new_role.role)}\n"
                f"Текущие союзники:\n{profiles}",
            )
            for player_id in game_data[new_role.roles_key]
        ),
        return_exceptions=True,
    )


async def send_messages_after_night(
    game_data: GameCache, bot: Bot, group_chat_id: int
):
    messages = game_data["messages_after_night"]
    if not messages:
        return
    number_of_night = make_build(
        f"Важнейшие события ночи {game_data['number_of_night']}:\n\n"
    )
    chats_and_messages = defaultdict(list)
    for chat_id, message in messages:
        chats_and_messages[chat_id].append(message)
    tasks = []
    for chat_id, messages in chats_and_messages.items():
        if chat_id != group_chat_id:
            tasks.append(
                bot.send_message(
                    chat_id=chat_id,
                    text=number_of_night
                    + "\n\n".join(
                        make_build(f"{number}) {message}")
                        for number, message in enumerate(
                            sorted(messages, key=len), start=1
                        )
                    ),
                )
            )
        else:
            for message in messages:
                tasks.append(
                    bot.send_message(
                        chat_id=chat_id, text=make_build(message)
                    )
                )
    await asyncio.gather(*tasks, return_exceptions=True)


async def send_request_to_vote(
    bot: Bot,
    game_data: GameCache,
    user_id: int,
    players_ids: LivePlayersIds,
    players: UsersInGame,
):
    sent_message = await bot.send_message(
        chat_id=user_id,
        text="Проголосуй за того, кто не нравится!",
        reply_markup=send_selection_to_players_kb(
            players_ids=players_ids,
            players=players,
            exclude=user_id,
            user_index_cb=UserVoteIndexCbData,
        ),
    )
    game_data["to_delete"].append([user_id, sent_message.message_id])


def remind_worden_about_inspections(game_data: GameCache):
    if not game_data["text_about_checked_for_the_same_groups"]:
        return "Нет информации о совместных группах"
    return (
        "По результатам прошлых проверок выяснено:\n\n"
        + game_data["text_about_checked_for_the_same_groups"]
    )


def remind_commissioner_about_inspections(
    game_data: GameCache,
) -> str:
    if not game_data["text_about_checks"]:
        return "Роли ещё неизвестны"
    return (
        "По результатам прошлых проверок выяснено:\n\n"
        + game_data["text_about_checks"]
    )
