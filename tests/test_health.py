from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers import health

app = FastAPI(title="testing API")
app.include_router(health.router)


client = TestClient(app)


def test_read_main():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
