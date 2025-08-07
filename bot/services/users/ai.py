from typing import TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.utils.chat_action import ChatActionSender

from general import settings
from general.commands import PrivateCommands
from services.base import RouterHelper
from utils.pretty_text import make_build
from html import escape

if TYPE_CHECKING:
    from ai.client import RAGSystem


class AIManager(RouterHelper):
    async def answer_question(
        self, ai: "RAGSystem", command: CommandObject
    ):
        question = command.args
        if not question:
            await self.message.reply(
                text=make_build(
                    "Некорректная форма отправки вопроса к AI ассистенту, пример:\n\n"
                )
                + f"/{PrivateCommands.q.name} Как работают ставки?"
            )
            return
        await self.message.answer(
            make_build(
                "🥺Пожалуйста, подождите!\n\n"
                "Ответ Mafia AI может генерироваться некоторое время..."
            )
        )
        async with ChatActionSender.typing(
            bot=self.message.bot,
            chat_id=self.message.from_user.id,
        ):
            response = await ai.query(question=question)
            if response == settings.ai.unavailable_message:
                text = response
            else:
                text = (
                    f"{response[:3950]}\n\n⚠️Ответ сгенерирован Mafia AI. "
                    f"Только для ознакомления."
                )
            await self.message.answer(escape(text))
