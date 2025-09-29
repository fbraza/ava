from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers import slack_agent

app = FastAPI(title="testing API")
app.include_router(slack_agent.router)


client = TestClient(app)
instructions = (
    "Post in the general channel that our team meeting will be delayed by 30 minutes"
)


def test_read_main():
    response = client.post("/slack", json={"user_instruction": f"{instructions}"})
    assert response.json() == {"status": "ok"}
