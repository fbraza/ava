from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers import slack_agent

app = FastAPI(title="testing API")
app.include_router(slack_agent.router)


client = TestClient(app)


def test_one_tool_one_message():
    instructions = "Post in the general channel that our team meeting will be delayed by 30 minutes"
    response = client.post("/slack", json={"user_instruction": f"{instructions}"})
    assert response.json()["status"] == "ok"


def test_two_tools_two_messages():
    instructions = "First post in the general channel that our team meeting for Monday is canceled. Next post in the sandbox channel that our team did a great job"
    response = client.post("/slack", json={"user_instruction": f"{instructions}"})
    assert response.json()["status"] == "ok"
