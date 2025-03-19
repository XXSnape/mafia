from sqlalchemy.orm import Mapped, mapped_column

from database.base import BaseModel


class GroupingModel(BaseModel):
    name: Mapped[str] = mapped_column(primary_key=True)
