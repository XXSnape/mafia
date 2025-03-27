from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import BaseModel, IdMixin


class OrderModel(IdMixin, BaseModel):
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(
        ForeignKey("roles.name", ondelete="CASCADE")
    )
    number: Mapped[int]
