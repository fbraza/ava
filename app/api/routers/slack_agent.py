import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from slack_sdk import WebClient

from app.tools import slack

_ = load_dotenv()

open_router_token = os.environ.get("OPEN_ROUTER_TOKEN", "")
slack_token = os.environ.get("SLACK_USER_TOKEN", "")
client = WebClient(token=slack_token)

prompt_path = Path(__file__).resolve().parents[2] / "pompts" / "slack.md"
prompt_instructions = prompt_path.read_text(encoding="utf-8")

model = OpenAIChatModel(
    "z-ai/glm-4.5",
    provider=OpenRouterProvider(api_key=open_router_token),
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
