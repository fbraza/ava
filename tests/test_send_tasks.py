import os

import pytest
from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError

from app.models import tools
from app.tools import slack

_ = load_dotenv()


@pytest.mark.parametrize(
    "channel,text,token",
    [
        (
            "sandbox",
            "Hello, AVA backend live smoke :rocket:",
            os.environ.get("SLACK_BOT_TOKEN"),
        ),
        (
            "general",
            "Hello, User is live smoke :rocket:",
            os.environ.get("SLACK_USER_TOKEN"),
        ),
    ],
)
def test_post_message_with_tool(channel: str, text: str, token: str | None):
    if token is not None:
        tool_params = tools.SlackChatPostMessageParams(channel=channel, text=text)
        try:
            response = slack.post_message(token=token, params=tool_params)
        except SlackApiError as exc:
            pytest.fail(f"Slack API error: {exc.response['error']}")

        assert response["ok"] is True
        assert response["message"]["text"] == text
        assert "ts" in response
