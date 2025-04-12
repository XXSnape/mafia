from cache.cache_types import RolesLiteral
from database.common.base import BaseModel, IdMixin
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class ResultModel(IdMixin, BaseModel):
    __table_args__ = (CheckConstraint("money >= 0"),)
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="SET NULL")
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE")
    )
    role_id: Mapped[RolesLiteral] = mapped_column(
        ForeignKey("roles.key", ondelete="SET NULL"),
    )
    is_winner: Mapped[bool]
    nights_lived: Mapped[int]
    money: Mapped[int]
