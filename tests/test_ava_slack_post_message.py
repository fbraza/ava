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
            response = slack.post_message(ctx=ctx, params=tool_params)
        except SlackApiError as exc:
            pytest.fail(f"Slack API error: {exc.response['error']}")

        assert response["status"] == 200
        assert response["result"] == "Message has been posted"
        assert response["channel"] == tool_params.channel
        assert response["msg"] == tool_params.text


def test_slack_tools_are_synced():
    token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=token)
    test_model = TestModel(call_tools=[])
    agent = Agent(test_model, toolsets=[slack.slack_toolset], deps_type=slack.Deps)
    _ = agent.run_sync("What tools are available?", deps=slack.Deps(client=client))

    assert [
        t.name for t in test_model.last_model_request_parameters.function_tools
    ] == ["slack.chat.postMessage"]
