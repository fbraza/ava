from dataclasses import dataclass

from pydantic_ai import RunContext
from pydantic_ai.toolsets import FunctionToolset
from slack_sdk import WebClient
from slack_sdk.web.slack_response import SlackResponse

from app.models.tools import SlackChatPostMessageParams


@dataclass
class Deps:
    client: WebClient


slack_toolset = FunctionToolset()


@slack_toolset.tool(name="slack.chat.postMessage")
def post_message(
    ctx: RunContext[Deps], params: SlackChatPostMessageParams
) -> SlackResponse:
    return ctx.deps.client.chat_postMessage(channel=params.channel, text=params.text)
