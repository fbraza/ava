from fastapi import FastAPI

from app.api.routers import health, slack_agent

app = FastAPI(title="AVA Agents", version="0.1.0")
app.include_router(health.router)
app.include_router(slack_agent.router)
