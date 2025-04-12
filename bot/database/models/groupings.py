from database.common.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column


class GroupingModel(BaseModel):
    name: Mapped[str] = mapped_column(primary_key=True)
