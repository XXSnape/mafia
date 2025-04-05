from pydantic import BaseModel

from cache.cache_types import RolesLiteral


class UserMoneySchema(BaseModel):
    user_tg_id: int
    money: int


class BidForRoleSchema(UserMoneySchema):
    role_id: RolesLiteral


class ResultBidForRoleSchema(BidForRoleSchema):
    is_winner: bool
    game_id: int


class RateSchema(BaseModel):
    user_tg_id: int
    money: int
    role_id: str
    is_winner: bool
    game_id: int
