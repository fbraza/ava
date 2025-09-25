from typing import Literal

from pydantic import BaseModel

from app.models.tools import SlackChatPostMessageParams


class Step(BaseModel):
    tool: Literal["slack.chat.postMessage"]
    params: SlackChatPostMessageParams


class Plan(BaseModel):
    steps: list[Step]
