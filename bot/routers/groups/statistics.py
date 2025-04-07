from datetime import timedelta

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import (
    Command,
    StateFilter,
)
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.games import GamesDao
from database.dao.groups import GroupsDao
from database.schemas.common import TgId, IdSchema
from database.schemas.groups import GroupIdSchema
from utils.tg import delete_message

router = Router(name=__name__)


@router.message(Command("statistics"))
async def get_group_statistics(
    message: Message, session_without_commit: AsyncSession
):
    await delete_message(message)
    group = await GroupsDao(
        session=session_without_commit
    ).find_one_or_none(TgId(tg_id=message.chat.id))
    if group is None:
        return

    number_of_games = 0
    number_of_nights = 0

    group_id_filter = GroupIdSchema(group_id=group.id)
    games_dao = GamesDao(session=session_without_commit)
    res = await games_dao.get_average_number_of_players(
        group_id_filter
    )
    print(res)
    # count =
    # game_result = await GamesDao(
    #     session=session_without_commit
    # ).get_results(group_id_filter)
    # if game_result is None:
    #     await message.answer("В этой группе еще не было игр!")
    #     return
    # text = (
    #     f"Количество игр: {game_result.number_of_games}" f"Средняя "
    # )
    # print(game_result)

    # if
    # groupings_text = "Статистика о группировках:\n"
    # games_dto = GamesDao(session=session_without_commit)
    # groupings_result = await games_dto.get_winning_groupings(
    #     group_id_filter
    # )
    # t = timedelta(seconds=23, microseconds=232)
    # t.total_seconds()
    # for row in game_result:
    #
    #     pass

    await message.answer("Hello!")
