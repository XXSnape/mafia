from pydantic import BaseModel


class SubscriptionSchema(BaseModel):
    user_tg_id: int
    group_id: int


class NotificationSchema(BaseModel):
    game_chat: int
    group_id: int
    title: str
