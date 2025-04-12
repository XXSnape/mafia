from cache.cache_types import RolesLiteral
from database.common.base import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class RoleModel(BaseModel):
    key: Mapped[RolesLiteral] = mapped_column(primary_key=True)
    grouping: Mapped[str] = mapped_column(
        ForeignKey("groupings.name", ondelete="RESTRICT")
    )
