from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from general.resources import Resources
from database.common.base import BaseModel


class AssetModel(BaseModel):
    __table_args__ = (CheckConstraint("cost > 0"),)
    name: Mapped[Resources] = mapped_column(primary_key=True)
    cost: Mapped[int]
