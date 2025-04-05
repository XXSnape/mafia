from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from cache.cache_types import RolesLiteral
from database.common.base import BaseModel


class RoleModel(BaseModel):
    key: Mapped[RolesLiteral] = mapped_column(primary_key=True)
    grouping: Mapped[str] = mapped_column(
        ForeignKey("groupings.name", ondelete="RESTRICT")
    )
