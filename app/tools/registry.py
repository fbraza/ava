from collections.abc import Callable

from slack_sdk.web.slack_response import SlackResponse

from app.models.tools import SlackChatPostMessageParams
from app.tools.slack import post_message

TOOLS: dict[str, dict[str, type | Callable[..., SlackResponse]]] = {
    "slack.chat.postMessage": {
        "schema": SlackChatPostMessageParams,
        "fn": post_message,
    },
}
