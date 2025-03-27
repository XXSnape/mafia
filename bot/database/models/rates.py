from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import IdMixin, BaseModel


class RateModel(IdMixin, BaseModel):
    money: Mapped[int]
    is_winner: Mapped[bool]
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE")
    )
    user_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(
        ForeignKey("roles.name", ondelete="CASCADE")
    )
