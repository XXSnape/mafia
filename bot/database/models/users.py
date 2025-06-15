from datetime import datetime

from database.common.base import BaseModel
from sqlalchemy import BigInteger, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(BaseModel):
    __table_args__ = (
        CheckConstraint("balance >= 0"),
        CheckConstraint("anonymous_letters >= 0"),
    )
    tg_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    balance: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0"
    )
    registration_date: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    anonymous_letters: Mapped[int] = mapped_column(
        default=0, server_default="0"
    )
    is_banned: Mapped[bool] = mapped_column(default=False)
