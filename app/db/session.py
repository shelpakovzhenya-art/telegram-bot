"""Database session management."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings
from app.db.base import create_session_maker

# Global session maker (will be initialized on first use)
_session_maker: None | type[AsyncSession] = None


def get_session_maker(settings: Settings) -> type[AsyncSession]:
    """Get or create session maker."""
    global _session_maker
    if _session_maker is None:
        _session_maker = create_session_maker(settings)
    return _session_maker


@asynccontextmanager
async def get_db_session(settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    session_maker = get_session_maker(settings)
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

