from typing import Literal

from pydantic import BaseModel

from app.models.tools import SlackChatPostMessageParams


class Step(BaseModel):
    """Single tool invocation within a plan."""

    tool: Literal["slack.chat.postMessage"]
    params: SlackChatPostMessageParams


class Plan(BaseModel):
    """Sequence of tool steps produced by the planner."""

    steps: list[Step]
