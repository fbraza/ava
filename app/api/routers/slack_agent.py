from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from slack_sdk import WebClient

from app.core.config import get_settings
from app.tools import slack

settings = get_settings()
client = WebClient(token=settings.slack_token or "")

prompt_path = Path(__file__).resolve().parents[2] / "pompts" / "slack.md"
prompt_instructions = prompt_path.read_text(encoding="utf-8")

model = OpenAIChatModel(
    settings.model_name,
    provider=OpenRouterProvider(api_key=settings.open_router_token or ""),
)

agent = Agent(
    model=model,
    deps_type=slack.Deps,
    instructions=prompt_instructions,
)


class Prompt(BaseModel):
    user_instruction: str


router = APIRouter()


@router.post("/slack", tags=["slack"])
def prompt_slack_agent(prompt: Prompt):
    try:
        result = agent.run_sync(
            f"{prompt.user_instruction}",
            deps=slack.Deps(client=client),
            toolsets=[slack.slack_toolset],  # type: ignore
        )
        return {"content": result.output, "status": "ok"}
    except Exception as e:
        return {"msg": str(e), "status": "failed"}
