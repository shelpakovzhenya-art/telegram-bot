"""Karma service."""
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings
from app.db.models import Karma, KarmaTransaction


class KarmaService:
    """Service for managing karma."""

    def __init__(self, settings: Settings) -> None:
        """Initialize karma service."""
        self.settings = settings
        self.cooldown_minutes = settings.KARMA_COOLDOWN_MINUTES

    async def get_karma(
        self, session: AsyncSession, user_id: int, chat_id: int
    ) -> int:
        """Get user karma in chat."""
        stmt = select(Karma).where(
            Karma.user_id == user_id, Karma.chat_id == chat_id
        )
        result = await session.execute(stmt)
        karma = result.scalar_one_or_none()
        return karma.karma if karma else 0

    async def add_karma(
        self,
        session: AsyncSession,
        from_user_id: int,
        to_user_id: int,
        chat_id: int,
    ) -> bool:
        """Add karma to user. Returns True if successful."""
        # No cooldown - always allow karma
        
        # Add karma transaction (for history, but not checking cooldown)
        transaction = KarmaTransaction(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            chat_id=chat_id,
        )
        session.add(transaction)

        # Update or create karma
        stmt = select(Karma).where(
            Karma.user_id == to_user_id, Karma.chat_id == chat_id
        )
        result = await session.execute(stmt)
        karma = result.scalar_one_or_none()

        if karma:
            karma.karma += 1
        else:
            karma = Karma(user_id=to_user_id, chat_id=chat_id, karma=1)
            session.add(karma)

        await session.commit()
        return True

    async def get_top_karma(
        self, session: AsyncSession, chat_id: int, limit: int = 10
    ) -> list[tuple[int, int]]:
        """Get top users by karma in chat. Returns list of (user_id, karma)."""
        stmt = (
            select(Karma.user_id, Karma.karma)
            .where(Karma.chat_id == chat_id)
            .order_by(Karma.karma.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.all())

