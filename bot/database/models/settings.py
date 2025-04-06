from sqlalchemy import ForeignKey, BigInteger, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

from database.common.base import BaseModel, IdMixin
from general import settings


class SettingModel(IdMixin, BaseModel):
    __table_args__ = (
        CheckConstraint("time_for_night > 10"),
        CheckConstraint("time_for_day > 10"),
    )
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    time_for_night: Mapped[int] = mapped_column(
        default=settings.mafia.time_for_night
    )
    time_for_day: Mapped[int] = mapped_column(
        default=settings.mafia.time_for_day
    )
