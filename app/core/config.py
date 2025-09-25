from pydantic import BaseModel


class Settings(BaseModel):
    slack_bot_token: str
    ai_provider: str = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
