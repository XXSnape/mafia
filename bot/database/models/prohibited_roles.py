from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import BaseModel, IdMixin


class ProhibitedRoleModel(IdMixin, BaseModel):
    __tablename__ = "prohibited_roles"
    user_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(
        ForeignKey("roles.name", ondelete="CASCADE")
    )
