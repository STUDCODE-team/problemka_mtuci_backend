import pytest
from datetime import datetime, timedelta, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import jwt
from httpx import ASGITransport, AsyncClient

from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_priority import ReportPriority
from domain.models.enums.report_status import ReportStatus
from domain.models.enums.report_type import ReportType
from domain.models.schemas.read_report import ReadReportDto, ReadReportListDto
from domain.models.schemas.comment import ReadCommentDto
from domain.models.schemas.status_history import ReadStatusHistoryDto

TEST_JWT_SECRET = "test-jwt-secret-key-at-least-32chars!!"


def make_access_token(user_id: str = None, role: str = "user") -> str:
    payload = {
        "sub": user_id or str(uuid4()),
        "role": role,
        "type": "access",
        "exp": datetime.now(UTC) + timedelta(minutes=15),
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


def make_report_dto(**kw) -> ReadReportDto:
    now = datetime.now(UTC)
    return ReadReportDto(
        id=kw.get("id", uuid4()),
        title=kw.get("title", "Test Report"),
        description=kw.get("description", "A description"),
        location=kw.get("location", "Building A"),
        room=kw.get("room", None),
        category=kw.get("category", ReportCategory.PLUMBING),
        priority=kw.get("priority", ReportPriority.MEDIUM),
        type=kw.get("type", ReportType.REPORT),
        status=kw.get("status", ReportStatus.NEW),
        reporter_id=kw.get("reporter_id", uuid4()),
        photo_url=kw.get("photo_url", None),
        created_at=kw.get("created_at", now),
        updated_at=kw.get("updated_at", None),
    )


def make_comment_dto(**kw) -> ReadCommentDto:
    return ReadCommentDto(
        id=kw.get("id", uuid4()),
        report_id=kw.get("report_id", uuid4()),
        author_id=kw.get("author_id", uuid4()),
        text=kw.get("text", "A comment"),
        created_at=kw.get("created_at", datetime.now(UTC)),
    )


@pytest.fixture
def mock_service():
    svc = MagicMock()
    svc.create_report = AsyncMock(return_value=make_report_dto())
    svc.get_report_by_id = AsyncMock(return_value=make_report_dto())
    svc.update_report = AsyncMock(return_value=make_report_dto())
    svc.delete_report = AsyncMock(return_value=None)
    svc.change_status = AsyncMock(return_value=make_report_dto())
    svc.force_change_status = AsyncMock(return_value=make_report_dto())
    svc.get_all_reports = AsyncMock(return_value=[])
    svc.get_my_reports = AsyncMock(return_value=[])
    svc.add_comment = AsyncMock(return_value=make_comment_dto())
    svc.get_comments = AsyncMock(return_value=[])
    svc.get_status_history = AsyncMock(return_value=[])
    svc.get_my_notifications = AsyncMock(return_value=[])
    svc.mark_notification_read = AsyncMock(return_value=True)
    svc.mark_all_notifications_read = AsyncMock(return_value=0)
    return svc


@pytest.fixture
async def client(mock_service):
    from api.dependencies import get_service
    from main import app

    app.dependency_overrides[get_service] = lambda: mock_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.pop(get_service, None)


# --- health ---

async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200


# --- /my (authenticated) ---

async def test_get_my_reports_without_auth_returns_401(client):
    response = await client.get("/my")
    assert response.status_code == 401


async def test_get_my_reports_returns_list(client):
    token = make_access_token(role="user")
    response = await client.get("/my", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# --- POST / ---

async def test_create_report_without_auth_returns_401(client):
    response = await client.post("/", json={
        "title": "T", "description": "D", "location": "L",
        "category": "plumbing",
    })
    assert response.status_code == 401


async def test_create_report_returns_201_or_200(client):
    token = make_access_token(role="user")
    response = await client.post(
        "/",
        json={
            "title": "Broken pipe",
            "description": "Water leaking from ceiling",
            "location": "Floor 3, Room 301",
            "category": "plumbing",
            "priority": "high",
            "type": "report",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 201)
    body = response.json()
    assert "id" in body
    assert "title" in body


async def test_create_report_validates_required_fields(client):
    token = make_access_token(role="user")
    response = await client.post(
        "/",
        json={"title": "Only title"},  # missing description, location, category
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


# --- GET / ---

async def test_get_reports_without_auth_returns_401(client):
    response = await client.get("/")
    assert response.status_code == 401


async def test_get_reports_returns_list(client):
    token = make_access_token(role="user")
    response = await client.get("/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# --- GET /{report_id} ---

async def test_get_report_by_id_returns_200(client):
    token = make_access_token(role="user")
    report_id = uuid4()
    response = await client.get(
        f"/{report_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


async def test_get_report_by_id_not_found_returns_404(client, mock_service):
    from fastapi import HTTPException
    mock_service.get_report_by_id.side_effect = HTTPException(status_code=404, detail="Not found")
    token = make_access_token(role="user")
    response = await client.get(
        f"/{uuid4()}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


# --- DELETE /{report_id} ---

async def test_delete_report_without_auth_returns_401(client):
    response = await client.delete(f"/{uuid4()}")
    assert response.status_code == 401


async def test_delete_report_returns_204(client):
    token = make_access_token(role="user")
    response = await client.delete(
        f"/{uuid4()}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204


# --- PATCH /{report_id}/status (manager) ---

async def test_change_status_requires_manager_or_admin(client):
    token = make_access_token(role="user")
    response = await client.patch(
        f"/{uuid4()}/status",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


async def test_change_status_as_manager_returns_200(client):
    token = make_access_token(role="manager")
    response = await client.patch(
        f"/{uuid4()}/status",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# --- PATCH /{report_id}/status/force (admin) ---

async def test_force_status_requires_admin(client):
    token = make_access_token(role="manager")
    response = await client.patch(
        f"/{uuid4()}/status/force",
        json={"status": "new"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


async def test_force_status_as_admin_returns_200(client):
    token = make_access_token(role="admin")
    response = await client.patch(
        f"/{uuid4()}/status/force",
        json={"status": "new"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# --- POST /{report_id}/comments ---

async def test_add_comment_returns_200(client):
    token = make_access_token(role="user")
    response = await client.post(
        f"/{uuid4()}/comments",
        json={"text": "This is a comment"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "text" in response.json()


async def test_add_empty_comment_returns_422(client):
    token = make_access_token(role="user")
    response = await client.post(
        f"/{uuid4()}/comments",
        json={"text": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


# --- GET /{report_id}/comments ---

async def test_get_comments_returns_list(client):
    token = make_access_token(role="user")
    response = await client.get(
        f"/{uuid4()}/comments",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# --- GET /{report_id}/history ---

async def test_get_status_history_returns_list(client):
    token = make_access_token(role="user")
    response = await client.get(
        f"/{uuid4()}/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
