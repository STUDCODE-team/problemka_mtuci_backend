import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import jwt
from httpx import ASGITransport, AsyncClient

TEST_JWT_SECRET = "test-jwt-secret-key-at-least-32chars!!"


def make_access_token(user_id: str = None, role: str = "user") -> str:
    payload = {
        "sub": user_id or str(uuid4()),
        "role": role,
        "type": "access",
        "exp": datetime.now(UTC) + timedelta(minutes=15),
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


@pytest.fixture
def mock_push_service():
    svc = MagicMock()
    svc.save_subscription = AsyncMock(return_value=None)
    svc.delete_subscription = AsyncMock(return_value=None)
    svc.send_push_to_user = AsyncMock(return_value=None)
    return svc


@pytest.fixture
async def client(mock_push_service):
    from api.dependencies import get_push_service
    from main import app

    app.dependency_overrides[get_push_service] = lambda: mock_push_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.pop(get_push_service, None)


# --- health ---

async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200


# --- GET /push/vapid-public-key ---

async def test_get_vapid_public_key_returns_key(client):
    response = await client.get("/push/vapid-public-key")
    assert response.status_code == 200
    body = response.json()
    assert "public_key" in body


# --- POST /push/subscribe ---

async def test_subscribe_without_auth_returns_401(client):
    response = await client.post(
        "/push/subscribe",
        json={
            "endpoint": "https://push.example.com/123",
            "p256dh": "key123",
            "auth": "authsecret",
        },
    )
    assert response.status_code == 401


async def test_subscribe_with_auth_returns_204(client, mock_push_service):
    token = make_access_token(role="user")
    response = await client.post(
        "/push/subscribe",
        json={
            "endpoint": "https://push.example.com/123",
            "p256dh": "key123",
            "auth": "authsecret",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
    mock_push_service.save_subscription.assert_awaited_once()


async def test_subscribe_saves_correct_endpoint(client, mock_push_service):
    token = make_access_token(role="user")
    endpoint = "https://push.example.com/unique-endpoint"

    await client.post(
        "/push/subscribe",
        json={"endpoint": endpoint, "p256dh": "k", "auth": "a"},
        headers={"Authorization": f"Bearer {token}"},
    )

    call_kwargs = mock_push_service.save_subscription.call_args[1]
    assert call_kwargs["endpoint"] == endpoint


# --- POST /push/unsubscribe ---

async def test_unsubscribe_without_auth_returns_401(client):
    response = await client.post(
        "/push/unsubscribe",
        json={
            "endpoint": "https://push.example.com/123",
            "p256dh": "key123",
            "auth": "authsecret",
        },
    )
    assert response.status_code == 401


async def test_unsubscribe_with_auth_returns_204(client, mock_push_service):
    token = make_access_token(role="user")
    response = await client.post(
        "/push/unsubscribe",
        json={
            "endpoint": "https://push.example.com/123",
            "p256dh": "key123",
            "auth": "authsecret",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
    mock_push_service.delete_subscription.assert_awaited_once()


async def test_subscribe_missing_fields_returns_422(client):
    token = make_access_token(role="user")
    response = await client.post(
        "/push/subscribe",
        json={"endpoint": "only-endpoint"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
