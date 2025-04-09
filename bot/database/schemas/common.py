from pydantic import BaseModel


class IdSchema(BaseModel):
    id: int


class TgIdSchema(BaseModel):
    tg_id: int


class UserTgIdSchema(BaseModel):
    user_tg_id: int
