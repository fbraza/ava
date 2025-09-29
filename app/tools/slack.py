from dataclasses import dataclass

from pydantic_ai import RunContext
from pydantic_ai.toolsets import FunctionToolset
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.models.tools import SlackChatPostMessageParams


@dataclass
class Deps:
    client: WebClient


slack_toolset = FunctionToolset()


@slack_toolset.tool(name="slack.chat.postMessage")
def post_message(ctx: RunContext[Deps], params: SlackChatPostMessageParams) -> dict:
    """
    Use this function to post a message in the specified channel
    """
    try:
        _ = ctx.deps.client.chat_postMessage(channel=params.channel, text=params.text)
        return {
            "status": 200,
            "result": "Message has been posted",
            "channel": f"{params.channel}",
            "msg": f"{params.text}",
        }
    except SlackApiError as exc:
        return {"status": 500, "Slack API error": f"{exc.response['error']}"}
