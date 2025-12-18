"""Application settings."""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Bot token (required)
    BOT_TOKEN: str

    # Database
    DATABASE_URL: Optional[str] = None

    # Chat filtering
    ALLOWED_CHAT_IDS: Optional[str] = None  # Comma-separated list of chat IDs

    # Karma settings
    KARMA_COOLDOWN_MINUTES: int = 60

    # Warning system settings
    WARN_LIMIT: int = 3
    MUTE_HOURS: int = 24

    # Greeting settings
    GREETING_COOLDOWN_MINUTES: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    def get_allowed_chat_ids(self) -> Optional[list[int]]:
        """Parse ALLOWED_CHAT_IDS into a list of integers."""
        if not self.ALLOWED_CHAT_IDS:
            return None
        try:
            return [int(chat_id.strip()) for chat_id in self.ALLOWED_CHAT_IDS.split(",")]
        except ValueError:
            return None

