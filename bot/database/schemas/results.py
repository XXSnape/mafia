from database.schemas.bids import UserMoneySchema


class PersonalResultSchema(UserMoneySchema):
    game_id: int
    role: str
    is_winner: bool
    nights_lived: int
    text: str
