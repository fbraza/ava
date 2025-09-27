from pydantic_ai.toolsets import FunctionToolset

from app.tools.slack import slack_toolset

TOOLS: dict[str, FunctionToolset] = {"slack.tools": slack_toolset}
