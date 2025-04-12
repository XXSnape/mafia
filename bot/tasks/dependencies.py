from typing import AsyncGenerator, TypeAlias, Annotated

from fast_depends import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.common.sessions import async_session_maker


async def get_session_with_commit() -> (
    AsyncGenerator[AsyncSession, None]
):
    """Асинхронная сессия с автоматическим коммитом."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


SessionWithCommitDep: TypeAlias = Annotated[
    AsyncSession, Depends(get_session_with_commit)
]
