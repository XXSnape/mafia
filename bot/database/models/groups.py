from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import BaseModel


class GroupModel(BaseModel):
    tg_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    setting_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("settings.id", ondelete="SET NULL"),
        default=None,
    )
