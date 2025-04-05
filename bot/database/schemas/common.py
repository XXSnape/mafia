from pydantic import BaseModel


class IdSchema(BaseModel):
    id: int


class TgId(BaseModel):
    tg_id: int


class UserTgId(BaseModel):
    user_tg_id: int
