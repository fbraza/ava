import os

import pytest
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, RunUsage
from pydantic_ai.models.test import TestModel
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.models import tools
from app.tools import slack

_ = load_dotenv()


def test_health_ava_can_post_message():
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
    assert response["message"]["text"] == message_text  # type: ignore
    assert "ts" in response


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
def test_post_message_with_ctx(channel: str, text: str, token: str | None):
    if token is not None:
        client = WebClient(token=token)
        ctx = RunContext(
            deps=slack.Deps(client=client),
            model=TestModel(),
            usage=RunUsage(),
        )
        tool_params = tools.SlackChatPostMessageParams(channel=channel, text=text)
        try:
            response = slack.post_message(ctx=ctx, params=tool_params)  # type: ignore
        except SlackApiError as exc:
            pytest.fail(f"Slack API error: {exc.response['error']}")

        assert response["ok"] is True
        assert response["message"]["text"] == text
        assert "ts" in response


def test_slack_tools_are_synced():
    test_model = TestModel()
    agent = Agent(test_model, toolsets=[slack.slack_toolset])
    _ = agent.run_sync("What tools are available?")
    assert [
        t.name for t in test_model.last_model_request_parameters.function_tools
    ] == ["slack.chat.postMessage"]
