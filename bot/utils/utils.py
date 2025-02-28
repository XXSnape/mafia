from aiogram.types import Message


def get_profile_link(message: Message) -> str:
    return f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>'
