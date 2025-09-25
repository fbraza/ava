from slack_sdk import WebClient
from slack_sdk.web.slack_response import SlackResponse

from app.models.tools import SlackChatPostMessageParams


def post_message(token: str, params: SlackChatPostMessageParams) -> SlackResponse:
    client = WebClient(token=token)
    return client.chat_postMessage(channel=params.channel, text=params.text)
