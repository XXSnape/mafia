import enum
from dataclasses import dataclass


@dataclass(frozen=True)
class Group:
    name: str
    payment: int | None


class Groupings(enum.Enum):
    criminals = Group(name="Мафия😈", payment=30)
    civilians = Group(name="Мирные жители🙂", payment=20)
    killer = Group(name="Независимые наёмники🔪", payment=35)
    other = Group(name="Иные👽", payment=None)
