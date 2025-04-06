from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import BaseModel, IdMixin


class GroupModel(IdMixin, BaseModel):
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    setting_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        default=None,
    )
