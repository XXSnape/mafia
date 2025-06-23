from cache.cache_types import RolesLiteral
from database.common.base import BaseModel, IdMixin
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class OrderModel(IdMixin, BaseModel):
    __table_args__ = (CheckConstraint("number > 0"),)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE")
    )
    role_id: Mapped[RolesLiteral] = mapped_column(
        ForeignKey("roles.key", ondelete="CASCADE")
    )
    number: Mapped[int]
