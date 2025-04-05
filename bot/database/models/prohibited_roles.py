from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from cache.cache_types import RolesLiteral
from database.common.base import BaseModel, IdMixin


class ProhibitedRoleModel(IdMixin, BaseModel):
    __tablename__ = "prohibited_roles"
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    role_id: Mapped[RolesLiteral] = mapped_column(
        ForeignKey("roles.key", ondelete="CASCADE")
    )
