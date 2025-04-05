from sqlalchemy import ForeignKey, BigInteger, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

from database.common.base import BaseModel, IdMixin


class SettingModel(IdMixin, BaseModel):
    __table_args__ = (
        CheckConstraint("time_for_night > 25"),
        CheckConstraint("time_for_day > 25"),
    )

    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    time_for_night: Mapped[int]
    time_for_day: Mapped[int]
