from sqlalchemy import ForeignKey, BigInteger, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import IdMixin, BaseModel


class RateModel(IdMixin, BaseModel):
    __table_args__ = (CheckConstraint("money > 0"),)
    money: Mapped[int]
    is_winner: Mapped[bool]
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE")
    )
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.key", ondelete="CASCADE")
    )
