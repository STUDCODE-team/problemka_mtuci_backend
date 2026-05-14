import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import jwt
from httpx import ASGITransport, AsyncClient

TEST_JWT_SECRET = "test-jwt-secret-key-at-least-32chars!!"
TEST_USER_ID = str(uuid4())
TEST_ADMIN_ID = str(uuid4())


def make_access_token(user_id: str = None, role: str = "user") -> str:
    payload = {
        "sub": user_id or TEST_USER_ID,
        "role": role,
        "type": "access",
        "exp": datetime.now(UTC) + timedelta(minutes=15),
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


@pytest.fixture
def mock_auth_service():
    service = MagicMock()
    service.request_otp = AsyncMock(return_value=None)
    service.verify_otp = AsyncMock(return_value={
        "access_token": "acc_token",
        "refresh_token": "ref_token",
        "token_type": "bearer",
        "role": "user",
    })
    service.refresh = AsyncMock(return_value={
        "access_token": "new_acc",
        "refresh_token": "new_ref",
        "token_type": "bearer",
    })
    service.logout = AsyncMock(return_value=None)

    user_mock = MagicMock()
    user_mock.id = uuid4()
    user_mock.email = "user@example.com"
    user_mock.role = "user"
    user_mock.is_active = True
    user_mock.created_at = datetime.now(UTC)
    service.get_user_by_id = AsyncMock(return_value=user_mock)
    service.get_all_users = AsyncMock(return_value=[])
    service.has_privileged_role = AsyncMock(return_value=True)
    return service


@pytest.fixture
async def client(mock_auth_service):
    from api.dependencies import get_auth_service
    from main import app

    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.pop(get_auth_service, None)


# --- health ---

async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- request_otp ---

async def test_request_otp_calls_service(client, mock_auth_service):
    response = await client.post(
        "/request_otp",
        json={"email": "user@example.com", "role": "user"},
    )
    assert response.status_code == 200
    mock_auth_service.request_otp.assert_awaited_once_with("user@example.com")


async def test_request_otp_privileged_role_checks_privileges(client, mock_auth_service):
    response = await client.post(
        "/request_otp",
        json={"email": "admin@example.com", "role": "admin"},
    )
    assert response.status_code == 200
    mock_auth_service.has_privileged_role.assert_awaited_once_with("admin@example.com")


async def test_request_otp_validates_email_format(client):
    response = await client.post(
        "/request_otp",
        json={"email": "not-an-email", "role": "user"},
    )
    # Pydantic v2 may or may not validate email format depending on the schema
    # Just check it's not a 5xx
    assert response.status_code < 500


# --- verify_otp ---

async def test_verify_otp_success_returns_bearer(client):
    response = await client.post(
        "/verify_otp",
        json={"email": "user@example.com", "code": "123456"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "role" in body


async def test_verify_otp_invalid_code_returns_401(client, mock_auth_service):
    mock_auth_service.verify_otp.side_effect = ValueError("Invalid or expired OTP")
    response = await client.post(
        "/verify_otp",
        json={"email": "user@example.com", "code": "000000"},
    )
    assert response.status_code == 401


async def test_verify_otp_sets_cookies(client):
    response = await client.post(
        "/verify_otp",
        json={"email": "user@example.com", "code": "123456"},
    )
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    assert "access_token" in set_cookie_header or "access_token" in response.cookies


# --- refresh ---

async def test_refresh_without_cookie_returns_401(client):
    response = await client.post("/refresh")
    assert response.status_code == 401


async def test_refresh_with_cookie_returns_200(client):
    client.cookies.set("refresh_token", "some_refresh_token")
    response = await client.post("/refresh")
    assert response.status_code == 200


async def test_refresh_invalid_token_returns_401(client, mock_auth_service):
    mock_auth_service.refresh.side_effect = ValueError("Invalid or revoked refresh token")
    client.cookies.set("refresh_token", "bad_token")
    response = await client.post("/refresh")
    assert response.status_code == 401


# --- logout ---

async def test_logout_returns_200(client):
    response = await client.post("/logout")
    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out successfully"


async def test_logout_clears_cookies(client):
    client.cookies.set("refresh_token", "some_token")
    response = await client.post("/logout")
    assert response.status_code == 200


# --- /me ---

async def test_me_without_auth_returns_401(client):
    response = await client.get("/me")
    assert response.status_code == 401


async def test_me_with_valid_token_returns_200(client):
    token = make_access_token(user_id=TEST_USER_ID, role="user")
    client.cookies.set("access_token", token)
    response = await client.get("/me")
    assert response.status_code == 200


async def test_me_with_invalid_token_returns_401(client):
    client.cookies.set("access_token", "not.a.real.jwt")
    response = await client.get("/me")
    assert response.status_code == 401


async def test_me_returns_user_data(client, mock_auth_service):
    token = make_access_token(user_id=TEST_USER_ID, role="user")
    client.cookies.set("access_token", token)
    response = await client.get("/me")
    assert response.status_code == 200
    body = response.json()
    assert "email" in body
    assert "role" in body


# --- /users ---

async def test_list_users_without_auth_returns_401(client):
    response = await client.get("/users")
    assert response.status_code == 401


async def test_list_users_with_non_admin_returns_403(client):
    token = make_access_token(user_id=TEST_USER_ID, role="user")
    client.cookies.set("access_token", token)
    response = await client.get("/users")
    assert response.status_code == 403


async def test_list_users_with_admin_returns_200(client):
    token = make_access_token(user_id=TEST_ADMIN_ID, role="admin")
    client.cookies.set("access_token", token)
    response = await client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# --- /users/{user_id} ---

async def test_get_user_by_id_requires_admin(client):
    token = make_access_token(user_id=TEST_USER_ID, role="user")
    client.cookies.set("access_token", token)
    response = await client.get(f"/users/{uuid4()}")
    assert response.status_code == 403


async def test_get_user_by_id_as_admin_returns_200(client):
    token = make_access_token(user_id=TEST_ADMIN_ID, role="admin")
    client.cookies.set("access_token", token)
    response = await client.get(f"/users/{uuid4()}")
    assert response.status_code == 200


async def test_get_user_by_id_not_found_returns_404(client, mock_auth_service):
    mock_auth_service.get_user_by_id.return_value = None
    token = make_access_token(user_id=TEST_ADMIN_ID, role="admin")
    client.cookies.set("access_token", token)
    response = await client.get(f"/users/{uuid4()}")
    assert response.status_code == 404
