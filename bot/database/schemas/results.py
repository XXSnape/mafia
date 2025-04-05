from cache.cache_types import RolesLiteral
from database.schemas.bids import UserMoneySchema


class PersonalResultSchema(UserMoneySchema):
    game_id: int
    role_id: RolesLiteral
    is_winner: bool
    nights_lived: int
    text: str
