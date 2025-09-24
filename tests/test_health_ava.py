import os

import pytest
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def test_health_ava_can_post_message():
    _ = load_dotenv()

    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        pytest.skip("SLACK_BOT_TOKEN not set; live Slack test skipped")

    client = WebClient(token=token)
    message_text = "AVA backend live smoke :rocket:"

    try:
        response = client.chat_postMessage(channel="sandbox", text=message_text)
    except SlackApiError as exc:
        pytest.fail(f"Slack API error: {exc.response['error']}")

    assert response["ok"] is True
    assert response["message"]["text"] == message_text
    assert "ts" in response
