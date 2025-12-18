"""Database base configuration."""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.settings import Settings

Base = declarative_base()


def get_database_url(settings: Settings) -> str:
    """Get database URL from settings."""
    if settings.DATABASE_URL:
        # If DATABASE_URL is provided, use it
        return settings.DATABASE_URL
    else:
        # Default to SQLite
        return "sqlite+aiosqlite:///./data/app.db"


async def init_db(settings: Settings) -> None:
    """Initialize database."""
    database_url = get_database_url(settings)
    engine = create_async_engine(database_url, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Close engine (it will be recreated when needed)
    await engine.dispose()


def create_session_maker(settings: Settings) -> async_sessionmaker[AsyncSession]:
    """Create session maker for database."""
    database_url = get_database_url(settings)
    engine = create_async_engine(database_url, echo=False)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

