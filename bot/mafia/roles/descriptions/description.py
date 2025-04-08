from dataclasses import dataclass


@dataclass
class RoleDescription:
    skill: str | None
    pay_for: list[str]
    limitations: list[str] | None = None
    features: list[str] | None = None
    wins_if: str = "Общая победа группировки"
