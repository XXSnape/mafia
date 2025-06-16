from dataclasses import dataclass
from enum import StrEnum
from typing import assert_never


@dataclass
class Asset:
    name: str
    description: str


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
                ),
            )

        case _:
            assert_never(resource)


def get_cost_of_discounted_resource(cost: int, count: int):
    return (count * cost) - ((count // 5) * cost)
