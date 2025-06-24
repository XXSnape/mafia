from cache.cache_types import RolesLiteral
from database.common.base import BaseModel, IdMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class ProhibitedRoleModel(IdMixin, BaseModel):
    __tablename__ = "prohibited_roles"
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE")
    )
    role_id: Mapped[RolesLiteral] = mapped_column(
        ForeignKey("roles.key", ondelete="CASCADE")
    )
