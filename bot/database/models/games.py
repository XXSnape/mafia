from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import BaseModel, IdMixin


class GameModel(IdMixin, BaseModel):
    chat_id: Mapped[int]
    start: Mapped[datetime]
    winner: Mapped[str | None] = mapped_column(
        ForeignKey("groupings.name", ondelete="SET NULL"),
        default=None,
    )
    number_of_nights: Mapped[int | None] = mapped_column(
        default=None
    )
    end: Mapped[datetime | None] = mapped_column(default=None)
