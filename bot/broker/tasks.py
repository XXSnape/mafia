from faststream import FastStream
from faststream.rabbit import RabbitBroker
from pydantic import BaseModel
import asyncio

from database.common.sessions import async_session_maker
from database.dao.groupings import GroupingDao
from general.config import broker

#
# @broker.subscriber("test")
# async def base_handler(body: Any):
#     async with async_session_maker() as s:
#         await GroupingDao(session=s).add_many(body)
#         await s.commit()


async def main():
    app = FastStream(broker)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
