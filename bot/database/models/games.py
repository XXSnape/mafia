from datetime import datetime

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import BaseModel, IdMixin


class GameModel(IdMixin, BaseModel):
    group_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("groups.id", ondelete="CASCADE")
    )
    winning_group: Mapped[str | None] = mapped_column(
        ForeignKey("groupings.name", ondelete="SET NULL"),
        default=None,
    )
    number_of_nights: Mapped[int | None] = mapped_column(
        default=None
    )
    start: Mapped[datetime]
    end: Mapped[datetime | None] = mapped_column(default=None)
