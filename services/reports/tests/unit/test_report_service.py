import pytest
from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_priority import ReportPriority
from domain.models.enums.report_status import ReportStatus
from domain.models.enums.report_type import ReportType
from domain.models.schemas.create_report import CreateReportDto
from domain.models.schemas.comment import CreateCommentDto
from domain.models.schemas.status_history import ChangeStatusDto
from services.report_service import ReportService


def make_report(**kw):
    now = datetime.now(UTC)
    return SimpleNamespace(
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


def make_comment(**kw):
    return SimpleNamespace(
        id=kw.get("id", uuid4()),
        report_id=kw.get("report_id", uuid4()),
        author_id=kw.get("author_id", uuid4()),
        text=kw.get("text", "A comment"),
        created_at=kw.get("created_at", datetime.now(UTC)),
    )


def make_history(**kw):
    return SimpleNamespace(
        id=kw.get("id", uuid4()),
        report_id=kw.get("report_id", uuid4()),
        old_status=kw.get("old_status", ReportStatus.NEW),
        new_status=kw.get("new_status", ReportStatus.IN_PROGRESS),
        changed_by=kw.get("changed_by", uuid4()),
        changed_at=kw.get("changed_at", datetime.now(UTC)),
    )


def make_notification(**kw):
    return SimpleNamespace(
        id=kw.get("id", uuid4()),
        reporter_id=kw.get("reporter_id", uuid4()),
        report_id=kw.get("report_id", uuid4()),
        report_title=kw.get("report_title", "Test Report"),
        old_status=kw.get("old_status", ReportStatus.NEW),
        new_status=kw.get("new_status", ReportStatus.IN_PROGRESS),
        is_read=kw.get("is_read", False),
        created_at=kw.get("created_at", datetime.now(UTC)),
    )


@pytest.fixture
def report_repo():
    repo = AsyncMock()
    repo.get = AsyncMock(return_value=None)
    repo.get_all = AsyncMock(return_value=[])
    repo.get_by_reporter = AsyncMock(return_value=[])
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def comment_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_report_id = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def history_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_report_id = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def notification_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_reporter = AsyncMock(return_value=[])
    repo.mark_read = AsyncMock(return_value=True)
    repo.mark_all_read = AsyncMock(return_value=3)
    return repo


@pytest.fixture
def service(report_repo, comment_repo, history_repo, notification_repo):
    return ReportService(
        report_repo=report_repo,
        comment_repo=comment_repo,
        history_repo=history_repo,
        notification_repo=notification_repo,
    )


# --- create_report ---

async def test_create_report_persists_and_returns_dto(service, report_repo):
    mock_report = make_report()
    report_repo.create.return_value = mock_report

    dto = CreateReportDto(
        title="Broken pipe",
        description="Water leaking",
        location="Floor 3",
        category=ReportCategory.PLUMBING,
    )

    result = await service.create_report(dto, reporter_id=uuid4())

    report_repo.create.assert_awaited_once()
    assert result.title == "Broken pipe" or result.title == mock_report.title


async def test_create_report_sets_status_to_new(service, report_repo):
    mock_report = make_report(status=ReportStatus.NEW)
    report_repo.create.return_value = mock_report

    dto = CreateReportDto(
        title="Issue",
        description="Details",
        location="Room 101",
        category=ReportCategory.ELECTRICAL,
    )

    result = await service.create_report(dto, reporter_id=uuid4())

    assert result.status == ReportStatus.NEW


# --- get_report_by_id ---

async def test_get_report_by_id_returns_dto(service, report_repo):
    mock_report = make_report()
    report_repo.get.return_value = mock_report

    result = await service.get_report_by_id(mock_report.id)

    report_repo.get.assert_awaited_once_with(mock_report.id)
    assert result.id == mock_report.id


async def test_get_report_by_id_raises_404_when_not_found(service, report_repo):
    from fastapi import HTTPException
    report_repo.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_report_by_id(uuid4())

    assert exc_info.value.status_code == 404


# --- delete_report ---

async def test_delete_report_calls_repo_delete(service, report_repo):
    mock_report = make_report()
    report_repo.get.return_value = mock_report

    await service.delete_report(mock_report.id)

    report_repo.delete.assert_awaited_once_with(mock_report)


async def test_delete_report_raises_404_when_not_found(service, report_repo):
    from fastapi import HTTPException
    report_repo.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_report(uuid4())

    assert exc_info.value.status_code == 404


# --- update_report ---

async def test_update_report_modifies_fields(service, report_repo):
    from domain.models.schemas.update_report import UpdateReportDto

    mock_report = make_report(title="Old Title")
    report_repo.get.return_value = mock_report
    report_repo.update.return_value = mock_report

    update_dto = UpdateReportDto(title="New Title")
    await service.update_report(mock_report.id, update_dto)

    assert mock_report.title == "New Title"
    report_repo.update.assert_awaited_once_with(mock_report)


# --- change_status ---

async def test_change_status_valid_transition(service, report_repo, history_repo, notification_repo):
    mock_report = make_report(status=ReportStatus.NEW)
    report_repo.get.return_value = mock_report
    report_repo.update.return_value = mock_report

    with patch("services.report_service.notification_client.send_push", new=AsyncMock()):
        result = await service.change_status(
            mock_report.id, ReportStatus.IN_PROGRESS, changed_by=uuid4()
        )

    assert mock_report.status == ReportStatus.IN_PROGRESS
    history_repo.create.assert_awaited_once()
    notification_repo.create.assert_awaited_once()


async def test_change_status_invalid_transition_raises_400(service, report_repo):
    from fastapi import HTTPException
    mock_report = make_report(status=ReportStatus.RESOLVED)
    report_repo.get.return_value = mock_report

    with pytest.raises(HTTPException) as exc_info:
        await service.change_status(
            mock_report.id, ReportStatus.NEW, changed_by=uuid4()
        )

    assert exc_info.value.status_code == 400


async def test_change_status_rejected_is_terminal(service, report_repo):
    from fastapi import HTTPException
    mock_report = make_report(status=ReportStatus.REJECTED)
    report_repo.get.return_value = mock_report

    with pytest.raises(HTTPException) as exc_info:
        await service.change_status(
            mock_report.id, ReportStatus.RESOLVED, changed_by=uuid4()
        )

    assert exc_info.value.status_code == 400


# --- force_change_status ---

async def test_force_change_status_bypasses_fsm(service, report_repo, history_repo, notification_repo):
    # RESOLVED is terminal in FSM, but force should work
    mock_report = make_report(status=ReportStatus.RESOLVED)
    report_repo.get.return_value = mock_report
    report_repo.update.return_value = mock_report

    with patch("services.report_service.notification_client.send_push", new=AsyncMock()):
        result = await service.force_change_status(
            mock_report.id, ReportStatus.NEW, changed_by=uuid4()
        )

    assert mock_report.status == ReportStatus.NEW
    history_repo.create.assert_awaited_once()


# --- add_comment ---

async def test_add_comment_creates_and_returns_dto(service, report_repo, comment_repo):
    mock_report = make_report()
    mock_comment = make_comment(report_id=mock_report.id)
    report_repo.get.return_value = mock_report
    comment_repo.create.return_value = mock_comment

    dto = CreateCommentDto(text="This is a comment")
    result = await service.add_comment(mock_report.id, dto, author_id=uuid4())

    comment_repo.create.assert_awaited_once()
    assert result.text == mock_comment.text


async def test_add_comment_raises_404_when_report_missing(service, report_repo):
    from fastapi import HTTPException
    report_repo.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.add_comment(uuid4(), CreateCommentDto(text="x"), author_id=uuid4())

    assert exc_info.value.status_code == 404


# --- get_comments ---

async def test_get_comments_returns_list(service, report_repo, comment_repo):
    mock_report = make_report()
    comments = [make_comment(report_id=mock_report.id) for _ in range(2)]
    report_repo.get.return_value = mock_report
    comment_repo.get_by_report_id.return_value = comments

    result = await service.get_comments(mock_report.id)

    assert len(result) == 2


async def test_get_comments_raises_404_when_report_missing(service, report_repo):
    from fastapi import HTTPException
    report_repo.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_comments(uuid4())

    assert exc_info.value.status_code == 404


# --- get_status_history ---

async def test_get_status_history_returns_list(service, report_repo, history_repo):
    mock_report = make_report()
    history = [make_history(report_id=mock_report.id) for _ in range(2)]
    report_repo.get.return_value = mock_report
    history_repo.get_by_report_id.return_value = history

    result = await service.get_status_history(mock_report.id)

    assert len(result) == 2


# --- notifications ---

async def test_get_my_notifications(service, notification_repo):
    reporter_id = uuid4()
    notifs = [make_notification(reporter_id=reporter_id) for _ in range(3)]
    notification_repo.get_by_reporter.return_value = notifs

    result = await service.get_my_notifications(reporter_id)

    assert len(result) == 3
    notification_repo.get_by_reporter.assert_awaited_once_with(reporter_id)


async def test_mark_notification_read(service, notification_repo):
    notification_repo.mark_read.return_value = True

    result = await service.mark_notification_read(uuid4(), uuid4())

    assert result is True


async def test_mark_all_notifications_read(service, notification_repo):
    notification_repo.mark_all_read.return_value = 5

    result = await service.mark_all_notifications_read(uuid4())

    assert result == 5
