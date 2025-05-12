import asyncio
from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Union

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from cache.cache_types import (
    GameCache,
    PlayersIds,
    UserIdInt,
    UsersInGame,
)
from general.groupings import Groupings
from general.text import MONEY_SYM, NUMBER_OF_NIGHT, SKIP
from keyboards.inline.callback_factory.recognize_user import (
    UserVoteIndexCbData,
)
from keyboards.inline.cb.cb_text import DONT_VOTE_FOR_ANYONE_CB
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from utils.common import add_message_to_delete, get_criminals_ids
from utils.pretty_text import (
    cut_off_old_text,
    make_build,
)
from utils.sorting import (
    sorting_by_number,
    sorting_by_rank,
)

if TYPE_CHECKING:
    from general.collection_of_roles import DataWithRoles
    from mafia.roles import RoleABC


def get_live_players(
    game_data: GameCache, all_roles: Union["DataWithRoles", str]
) -> tuple[str, str]:
    profiles = get_profiles(
        players_ids=game_data["live_players_ids"],
        players=game_data["players"],
    )
    live_roles = get_live_roles(
        game_data=game_data, all_roles=all_roles
    )
    return (
        (
            f"{make_build(f'💗Живые игроки '
                      f'({len(game_data["live_players_ids"])}):')}\n"
            f"{profiles}\n\n{live_roles}"
        ),
        live_roles,
    )


def get_live_roles(
    game_data: GameCache, all_roles: Union["DataWithRoles", str]
):
    if isinstance(all_roles, str):
        return all_roles

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
        grouping_roles = "\n● ".join(
            sorted(role for role, _ in roles)
        )
        total = sum(count for _, count in roles)
        total_text = make_build(f"- {total}:")
        result += f"\n{grouping.value.name} {total_text}\n● {grouping_roles}\n"
    composition_of_groupings = (
        "👥Состав группировок:"
        if game_data["settings"]["show_roles_after_death"]
        else "👥Изначальный состав группировок во время Тумана Войны:"
    )
    return f"{make_build(composition_of_groupings)}\n" + result


def get_profiles(
    players_ids: PlayersIds,
    players: UsersInGame,
    show_current_roles: bool = False,
    show_initial_roles: bool = False,
    show_money: bool = False,
    sorting_factory: Callable | None = sorting_by_number,
    if_there_are_no_players: str = "\nПока нет участников!",
) -> str:
    if sorting_factory:
        sorting_func = sorting_factory(players=players)
        users = sorted(players_ids, key=sorting_func)
    else:
        users = players_ids
    result = ""
    if not users:
        return if_there_are_no_players
    for index, user_id in enumerate(users, 1):
        url = players[str(user_id)]["url"]
        number = players[str(user_id)].get("number", index)
        if show_current_roles:
            if show_initial_roles:
                show_current_roles = players[str(user_id)][
                    "initial_role"
                ]
            else:
                show_current_roles = players[str(user_id)][
                    "pretty_role"
                ]
            if show_money:
                money = players[str(user_id)]["money"]
                result += f"\n{number}) {url} — {show_current_roles} ({money}{MONEY_SYM})"
            else:
                result += f"\n{number}) {url} — {show_current_roles}"
        else:
            result += f"\n{number}) {url}"
    return make_build(result)


def get_profiles_during_registration(
    live_players_ids: PlayersIds, players: UsersInGame
) -> str:
    profiles = get_profiles(live_players_ids, players)
    return make_build(
        f"❤️Скорее присоединяйся к игре!\n\n"
        f"👥Участники:\n{profiles}"
    )


def get_results_of_goal_identification(game_data: GameCache):
    def sorting_by_voting(voting_data):
        return len(voting_data[1])

    result = make_build(
        f"📊Результаты голосования дня {game_data['number_of_night']}:"
    )

    vote_for = game_data["vote_for"]
    voting = defaultdict(list)
    for voting_id, voted_id in vote_for:
        voting[game_data["players"][str(voted_id)]["url"]].append(
            voting_id
        )

    voting_result = ""
    refused_result = ""
    if game_data["refused_to_vote"]:
        refused_result = (
            f"\n\n❤️Искренние ценители человеческой жизни "
            f"({len(game_data['refused_to_vote'])}):"
        )
        if game_data["settings"]["show_usernames_during_voting"]:
            refused_result += get_profiles(
                players_ids=game_data["refused_to_vote"],
                players=game_data["players"],
            )
        else:
            refused_result += "\n???"

    if not voting:
        voting_result = make_build(
            "\n\n😯Сегодня нет потенциальных жертв!"
        )
        return result + refused_result + voting_result
    for voted, voting_people in sorted(
        voting.items(), key=sorting_by_voting, reverse=True
    ):
        if game_data["settings"]["show_usernames_during_voting"]:
            text = get_profiles(
                players_ids=voting_people,
                players=game_data["players"],
            )
        else:
            text = "\n???"
        voting_result += (
            f"\n\n📝Голосовавшие за {voted} ({len(voting_people)}):"
            + text
        )

    return result + voting_result + refused_result


def get_results_of_voting(
    game_data: GameCache, removed_user_id: UserIdInt
):
    if not removed_user_id:
        return make_build(
            "🤯Доброта или банальная несогласованность? "
            "Посмотрим, воспользуются ли преступники таким подарком."
        )

    user_url = game_data["players"][str(removed_user_id)]["url"]
    pros = len(game_data["pros"])
    cons = len(game_data["cons"])

    show_users = game_data["settings"][
        "show_usernames_after_confirmation"
    ]
    if show_users and pros:
        voted_for_text = get_profiles(
            players_ids=list(set(game_data["pros"])),
            players=game_data["players"],
        )
    else:
        voted_for_text = ""
    if show_users and cons:
        voted_against_text = get_profiles(
            players_ids=list(set(game_data["cons"])),
            players=game_data["players"],
        )
    else:
        voted_against_text = ""

    text = (
        "Подводим итоги судьбы {user_url}:\n\n"
        "✅За линчевание - {pros}{voted_for_text}\n\n❌Против - {cons}{voted_against_text}\n\n"
    ).format(
        user_url=user_url,
        pros=pros,
        voted_for_text=voted_for_text,
        cons=cons,
        voted_against_text=voted_against_text,
    )

    return make_build(text)


async def notify_aliases_about_transformation(
    game_data: GameCache,
    bot: Bot,
    new_role: "RoleABC",
    user_id: int,
):
    url = game_data["players"][str(user_id)]["url"]
    initial_role = game_data["players"][str(user_id)]["initial_role"]
    if new_role.grouping == Groupings.criminals:
        users = get_criminals_ids(game_data)
    else:
        users = game_data[new_role.roles_key]
    profiles = get_profiles(
        players_ids=users,
        players=game_data["players"],
        show_current_roles=True,
        sorting_factory=sorting_by_rank,
    )
    await asyncio.gather(
        *(
            bot.send_photo(
                chat_id=player_id,
                photo=new_role.photo,
                caption=NUMBER_OF_NIGHT.format(
                    game_data["number_of_night"]
                )
                + f"{initial_role} {url} превратился в "
                f"{new_role.pretty_role}\n\n"
                f"Все текущие союзники и сокомандники:\n{profiles}",
            )
            for player_id in users
        ),
        return_exceptions=True,
    )


async def send_messages_after_night(
    game_data: GameCache, bot: Bot, group_chat_id: int
):
    messages = game_data["messages_after_night"]
    if not messages:
        return
    number_of_night = (
        f"Важнейшие события ночи {game_data['number_of_night']}:\n\n"
    )
    chats_and_messages = defaultdict(list)
    for chat_id, message in messages:
        chats_and_messages[chat_id].append(message)

    tasks = []
    if (
        game_data["settings"][
            "show_information_about_guests_at_night"
        ]
        is False
    ):
        for chat_id, _ in chats_and_messages.items():
            if chat_id != group_chat_id:
                tasks.append(
                    bot.send_message(
                        chat_id=chat_id,
                        text=make_build(
                            number_of_night
                            + "К тебе определенно кто-то приходил, но Туман Войны скрыл это..."
                        ),
                        protect_content=game_data["settings"][
                            "protect_content"
                        ],
                    )
                )
    else:
        for chat_id, messages in chats_and_messages.items():
            if chat_id != group_chat_id:
                tasks.append(
                    bot.send_message(
                        chat_id=chat_id,
                        text=make_build(
                            number_of_night
                            + "\n\n".join(
                                f"{number}) {message}"
                                for number, message in enumerate(
                                    sorted(messages, key=len),
                                    start=1,
                                )
                            )
                        ),
                        protect_content=game_data["settings"][
                            "protect_content"
                        ],
                    )
                )
            elif game_data["settings"]["show_roles_after_death"]:
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
    players_ids: PlayersIds,
    players: UsersInGame,
):
    game_data["waiting_for_action_at_day"].append(user_id)
    sent_message = await bot.send_message(
        chat_id=user_id,
        text=make_build(
            f"Проголосуй за того, кто угрожает твоим интересам, "
            f"или нажми на нижнюю кнопку «{SKIP}»!"
        ),
        reply_markup=send_selection_to_players_kb(
            players_ids=players_ids,
            players=players,
            exclude=user_id,
            user_index_cb=UserVoteIndexCbData,
            extra_buttons=(
                InlineKeyboardButton(
                    text=SKIP, callback_data=DONT_VOTE_FOR_ANYONE_CB
                ),
            ),
        ),
    )
    add_message_to_delete(
        game_data=game_data,
        chat_id=user_id,
        message_id=sent_message.message_id,
    )


async def send_a_lot_of_messages_safely(
    bot: Bot,
    users: list[UserIdInt],
    text: str,
    protect_content: bool,
    exclude: Iterable[UserIdInt] = (),
):
    await asyncio.gather(
        *(
            bot.send_message(
                chat_id=user_id,
                text=text,
                protect_content=protect_content,
            )
            for user_id in users
            if user_id not in exclude
        ),
        return_exceptions=True,
    )


def remind_worden_about_inspections(game_data: GameCache):
    if not game_data["text_about_checked_for_the_same_groups"]:
        return "Нет информации о совместных группах"

    text = game_data["text_about_checked_for_the_same_groups"]
    if len(text) > 3700:
        text = cut_off_old_text(text)
        game_data["text_about_checked_for_the_same_groups"] = text
    return "По результатам прошлых проверок выяснено:\n\n" + text


def remind_criminals_about_inspections(
    game_data: GameCache,
):
    users = [
        user_id
        for user_id in game_data.get("mafias_are_shown", [])
        if user_id in game_data["live_players_ids"]
    ]
    if not users:
        return
    profiles = get_profiles(
        players_ids=users,
        players=game_data["players"],
        show_current_roles=True,
    )
    return "По результатам прошлых проверок выяснено:\n" + profiles


def remind_commissioner_about_inspections(
    game_data: GameCache,
) -> str:
    if not game_data["text_about_checks"]:
        return "Роли ещё неизвестны"
    text = game_data["text_about_checks"]
    if len(text) > 3700:
        text = cut_off_old_text(text)
        game_data["text_about_checks"] = text
    return "По результатам прошлых проверок выяснено:\n\n" + text
