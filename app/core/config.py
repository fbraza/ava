from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    """
    Centralized application settings with lightweight env loading.

    This avoids a hard dependency on pydantic-settings while still validating
    types and providing a single import for configuration across the app.
    """

    # AI model (via OpenRouter's OpenAI-compatible interface)
    model_name: str = "z-ai/glm-4.5"

    # Provider tokens/keys
    open_router_token: str | None = None

    # Slack tokens
    slack_user_token: str | None = None
    slack_bot_token: str | None = None

    @property
    def slack_token(self) -> str | None:
        """
        Preferred Slack token to use for API calls.
        Prioritize user token when available, otherwise use bot token.
        """
        return self.slack_user_token or self.slack_bot_token


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Load settings from environment (and .env) once and cache them.
    """
    load_dotenv()

    return Settings(
        model_name=os.getenv("MODEL_NAME", "z-ai/glm-4.5"),
        open_router_token=os.getenv("OPEN_ROUTER_TOKEN"),
        slack_user_token=os.getenv("SLACK_USER_TOKEN"),
        slack_bot_token=os.getenv("SLACK_BOT_TOKEN"),
    )
