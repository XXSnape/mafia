from contextlib import suppress
from typing import cast

from aiogram.exceptions import TelegramAPIError
from cache.cache_types import StagesOfGameLiteral
from database.dao.groups import GroupsDao
from database.schemas.settings import TimeOfDaySchema
from keyboards.inline.callback_factory.settings import (
    TimeOfDayCbData,
)
from keyboards.inline.cb.cb_text import (
    TIME_FOR_CONFIRMATION_CB,
    TIME_FOR_DAY_CB,
    TIME_FOR_NIGHT_CB,
    TIME_FOR_VOTING_CB,
)
from keyboards.inline.keypads.time import (
    adjust_time_kb,
    select_stage_of_game_kb,
)
from services.base import RouterHelper
from utils.pretty_text import make_build


class TimeRouter(RouterHelper):

    async def select_stage_of_game(self):
        await self.callback.message.edit_text(
            make_build("⏳Выбери интересующий этап игры"),
            reply_markup=select_stage_of_game_kb(),
        )

    async def edit_game_time(self):
        group_schema = await self.get_group_id_schema(id_schema=True)
        group = await GroupsDao(
            session=self.session
        ).find_one_or_none(group_schema)
        stage_of_game = cast(StagesOfGameLiteral, self.callback.data)
        texts = {
            TIME_FOR_NIGHT_CB: "Выбери, сколько должна длиться ночь",
            TIME_FOR_DAY_CB: "Выбери, сколько должен длиться день",
            TIME_FOR_VOTING_CB: "Выбери, сколько должно длиться голосование для дальнейшего повешения",
            TIME_FOR_CONFIRMATION_CB: "Выбери, сколько должен длиться процесс подтверждения о повешении",
        }
        current_time = getattr(group, stage_of_game)
        message = texts[stage_of_game]
        await self.callback.message.edit_text(
            text=make_build(message),
            reply_markup=adjust_time_kb(
                stage_of_game=stage_of_game,
                current_time=current_time,
            ),
        )

    async def changes_length_of_time_of_day(
        self,
        callback_data: TimeOfDayCbData,
    ):
        value = TimeOfDaySchema(
            **{callback_data.stage_of_game: callback_data.seconds}
        )
        group_schema = await self.get_group_id_schema(id_schema=True)
        await GroupsDao(session=self.session).update(
            filters=group_schema,
            values=value,
        )
        with suppress(TelegramAPIError):
            await self.callback.message.edit_reply_markup(
                reply_markup=adjust_time_kb(
                    current_time=callback_data.seconds,
                    stage_of_game=callback_data.stage_of_game,
                )
            )
        await self.callback.answer()
