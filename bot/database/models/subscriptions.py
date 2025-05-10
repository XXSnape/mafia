from database.common.base import BaseModel, IdMixin
from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class SubscriptionModel(IdMixin, BaseModel):
    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "user_tg_id",
            name="idx_uniq_group_user",
        ),
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE")
    )
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE")
    )
