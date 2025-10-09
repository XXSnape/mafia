from dataclasses import dataclass
from enum import StrEnum
from typing import assert_never

from utils.pretty_text import make_pretty


@dataclass
class Asset:
    name: str
    description: str
    cost: int


class Resources(StrEnum):
    anonymous_letters = "anonymous_letters"


def get_data_about_resource(resource: Resources) -> Asset:
    match resource:
        case Resources.anonymous_letters:
            return Asset(
                name="💌Анонимки",
                description=(
                    "💌Анонимки позволяют отправлять сообщения в группу, "
                    "где проходит игра, от лица бота.\n"
                    "Сообщения будут доставлены, если игрок еще жив.\n\n"
                    f'Чтобы отправить анонимку, напишите в бота: {make_pretty('/anon "Ваше сообщение"')}\n\n'
                    f"Пример сообщения:\n"
                    f"<blockquote>😱😱😱НЕИЗВЕСТНЫЙ ОТПРАВИТЕЛЬ\n\n"
                    f'"Ваше сообщение"</blockquote>'
                ),
                cost=750,
            )

        case _:
            assert_never(resource)


def get_cost_of_discounted_resource(
    cost: int, count: int
) -> tuple[int, int]:
    discounts = {
        20: 45,
        15: 40,
        10: 35,
        5: 25,
        3: 10,
        1: 0,
    }
    discount = 0
    for total, discount in discounts.items():
        if count >= total:
            break
    return round((count * cost) * ((100 - discount) / 100)), discount
