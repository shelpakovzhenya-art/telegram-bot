"""Warning service."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings
from app.db.models import Warning


class WarnService:
    """Service for managing warnings."""

    def __init__(self, settings: Settings) -> None:
        """Initialize warn service."""
        self.settings = settings
        self.warn_limit = settings.WARN_LIMIT
        self.mute_hours = settings.MUTE_HOURS

    async def get_warn_count(
        self, session: AsyncSession, user_id: int, chat_id: int
    ) -> int:
        """Get warning count for user in chat."""
        stmt = (
            select(func.count(Warning.id))
            .where(Warning.user_id == user_id, Warning.chat_id == chat_id)
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def add_warning(
        self,
        session: AsyncSession,
        user_id: int,
        chat_id: int,
        admin_id: int,
        reason: str | None = None,
    ) -> int:
        """Add warning to user. Returns new warning count."""
        warning = Warning(
            user_id=user_id,
            chat_id=chat_id,
            admin_id=admin_id,
            reason=reason,
        )
        session.add(warning)
        await session.commit()

        return await self.get_warn_count(session, user_id, chat_id)

    async def remove_warning(
        self, session: AsyncSession, user_id: int, chat_id: int
    ) -> int:
        """Remove one warning from user. Returns new warning count."""
        stmt = (
            select(Warning)
            .where(Warning.user_id == user_id, Warning.chat_id == chat_id)
            .order_by(Warning.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        warning = result.scalar_one_or_none()

        if warning:
            await session.delete(warning)
            await session.commit()

        return await self.get_warn_count(session, user_id, chat_id)

    async def should_mute(
        self, session: AsyncSession, user_id: int, chat_id: int
    ) -> bool:
        """Check if user should be muted (reached warn limit)."""
        count = await self.get_warn_count(session, user_id, chat_id)
        return count >= self.warn_limit

