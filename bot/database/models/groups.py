from database.common.base import BaseModel, IdMixin
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class GroupModel(IdMixin, BaseModel):
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    setting_id: Mapped[int | None] = mapped_column(
        ForeignKey("settings.id", ondelete="SET NULL"),
        default=None,
    )
