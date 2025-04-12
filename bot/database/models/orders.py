from cache.cache_types import RolesLiteral
from database.common.base import BaseModel, IdMixin
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class OrderModel(IdMixin, BaseModel):
    __table_args__ = (CheckConstraint("number > 0"),)
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    role_id: Mapped[RolesLiteral] = mapped_column(
        ForeignKey("roles.key", ondelete="CASCADE")
    )
    number: Mapped[int]
