from database.dao.settings import SettingsDao
from database.schemas.common import UserTgId
from database.schemas.settings import TimeOfDaySchema
from keyboards.inline.callback_factory.settings import (
    TimeOfDay,
    TimeOfDayCbData,
)
from keyboards.inline.cb.cb_text import LENGTH_OF_NIGHT_CB
from keyboards.inline.keypads.settings import adjust_time_kb
from services.base import RouterHelper
from utils.pretty_text import make_build


class TimeRouter(RouterHelper):
    async def edit_game_time(self):
        setting = await SettingsDao(
            session=self.session
        ).find_one_or_none(
            UserTgId(user_tg_id=self.callback.from_user.id)
        )

        if self.callback.data == LENGTH_OF_NIGHT_CB:
            current_time = setting.time_for_night
            time_of_day = TimeOfDay.night
            message = (
                "Выбери, сколько в секундах должна длиться ночь"
            )
        else:
            current_time = setting.time_for_day
            time_of_day = TimeOfDay.day
            message = (
                "Выбери, сколько в секундах должен длиться день"
            )
        await self.callback.message.edit_text(
            text=make_build(message),
            reply_markup=adjust_time_kb(
                current_time=current_time, time_of_day=time_of_day
            ),
        )

    async def changes_length_of_time_of_day(
        self,
        callback_data: TimeOfDayCbData,
    ):
        value = TimeOfDaySchema()
        if callback_data.time_of_day == TimeOfDay.day:
            value.time_for_day = callback_data.seconds
        else:
            value.time_for_night = callback_data.seconds
        await SettingsDao(session=self.session).update(
            UserTgId(
                user_tg_id=self.callback.from_user.id,
            ),
            values=value,
        )
        await self.callback.message.edit_reply_markup(
            reply_markup=adjust_time_kb(
                current_time=callback_data.seconds,
                time_of_day=callback_data.time_of_day,
            )
        )
