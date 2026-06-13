import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from domain.models.enums.user_roles import UserRole
from domain.models.schemas.user_info import UserInfoDto
from services.auth_service import AuthService


def make_mock_user(email: str = "user@example.com", user_id: UUID = None) -> MagicMock:
    user = MagicMock()
    user.id = user_id or uuid4()
    user.email = email
    user.is_active = True
    user.created_at = datetime.now(UTC)
    return user


@pytest.fixture
def user_repo():
    repo = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=None)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    repo.get_effective_role = AsyncMock(return_value="user")
    repo.update_role = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def refresh_repo():
    repo = AsyncMock()
    repo.save = AsyncMock()
    repo.find_active_by_jti = AsyncMock(return_value=None)
    repo.revoke_by_jti = AsyncMock()
    return repo


@pytest.fixture
def otp_service():
    svc = AsyncMock()
    svc.create_otp = AsyncMock()
    svc.verify_otp = AsyncMock(return_value=True)
    return svc


@pytest.fixture
def token_service():
    svc = MagicMock()
    svc.create_access_token = MagicMock(return_value="access_token_str")
    svc.generate_refresh_token = MagicMock(return_value=("refresh_token_str", "jti_str"))
    svc.validate_refresh_token = MagicMock(return_value={"jti": "some_jti", "sub": str(uuid4())})
    return svc


@pytest.fixture
def auth_service(user_repo, refresh_repo, otp_service, token_service):
    return AuthService(
        user_repo=user_repo,
        refresh_repo=refresh_repo,
        otp_service=otp_service,
        token_service=token_service,
    )


# --- request_otp ---

async def test_request_otp_delegates_to_otp_service(auth_service, otp_service):
    await auth_service.request_otp("user@example.com")

    otp_service.create_otp.assert_awaited_once_with("user@example.com")


# --- verify_otp ---

async def test_verify_otp_raises_on_invalid_otp(auth_service, otp_service):
    otp_service.verify_otp.return_value = False

    with pytest.raises(ValueError, match="Invalid or expired OTP"):
        await auth_service.verify_otp("user@example.com", "000000")


async def test_verify_otp_creates_user_when_not_exists(auth_service, user_repo, token_service):
    new_user = make_mock_user("new@example.com")
    user_repo.get_by_email.return_value = None
    user_repo.create.return_value = new_user

    result = await auth_service.verify_otp("new@example.com", "123456")

    user_repo.create.assert_awaited_once_with("new@example.com")
    assert result["access_token"] == "access_token_str"
    assert result["refresh_token"] == "refresh_token_str"
    assert result["token_type"] == "bearer"


async def test_verify_otp_uses_existing_user(auth_service, user_repo):
    existing_user = make_mock_user()
    user_repo.get_by_email.return_value = existing_user

    result = await auth_service.verify_otp("user@example.com", "123456")

    user_repo.create.assert_not_awaited()
    assert "access_token" in result
    assert "refresh_token" in result


async def test_verify_otp_saves_refresh_token(auth_service, refresh_repo, user_repo):
    user = make_mock_user()
    user_repo.get_by_email.return_value = user

    await auth_service.verify_otp("user@example.com", "123456")

    refresh_repo.save.assert_awaited_once()


async def test_verify_otp_includes_role_in_result(auth_service, user_repo):
    user = make_mock_user()
    user_repo.get_by_email.return_value = user
    user_repo.get_effective_role.return_value = "manager"

    result = await auth_service.verify_otp("user@example.com", "123456")

    assert result["role"] == "manager"


# --- refresh ---

async def test_refresh_raises_when_record_not_found(auth_service, refresh_repo, token_service):
    user_id = str(uuid4())
    token_service.validate_refresh_token.return_value = {"jti": "jti_str", "sub": user_id}
    refresh_repo.find_active_by_jti.return_value = None

    with pytest.raises(ValueError, match="Invalid or revoked refresh token"):
        await auth_service.refresh("some_token")


async def test_refresh_raises_on_user_id_mismatch(auth_service, refresh_repo, token_service):
    user_id = str(uuid4())
    token_service.validate_refresh_token.return_value = {"jti": "jti_str", "sub": user_id}

    old_record = MagicMock()
    old_record.user_id = uuid4()  # different UUID
    refresh_repo.find_active_by_jti.return_value = old_record

    with pytest.raises(ValueError, match="Invalid or revoked refresh token"):
        await auth_service.refresh("mismatched_token")


async def test_refresh_returns_new_tokens_and_revokes_old(
    auth_service, refresh_repo, token_service, user_repo
):
    user_id_str = str(uuid4())
    user_id_uuid = UUID(user_id_str)

    token_service.validate_refresh_token.return_value = {
        "jti": "old_jti",
        "sub": user_id_str,
    }
    old_record = MagicMock()
    old_record.user_id = user_id_uuid
    refresh_repo.find_active_by_jti.return_value = old_record

    user = make_mock_user(user_id=user_id_uuid)
    user_repo.get_by_id.return_value = user

    result = await auth_service.refresh("valid_token")

    refresh_repo.revoke_by_jti.assert_awaited_once_with("old_jti")
    refresh_repo.save.assert_awaited_once()
    assert "access_token" in result
    assert "refresh_token" in result


async def test_refresh_raises_when_user_not_found(auth_service, refresh_repo, token_service, user_repo):
    user_id_str = str(uuid4())
    user_id_uuid = UUID(user_id_str)

    token_service.validate_refresh_token.return_value = {
        "jti": "jti_str",
        "sub": user_id_str,
    }
    old_record = MagicMock()
    old_record.user_id = user_id_uuid
    refresh_repo.find_active_by_jti.return_value = old_record
    user_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="User not found"):
        await auth_service.refresh("valid_token")


# --- logout ---

async def test_logout_revokes_jti(auth_service, refresh_repo, token_service):
    token_service.validate_refresh_token.return_value = {"jti": "target_jti"}

    await auth_service.logout("some_refresh_token")

    refresh_repo.revoke_by_jti.assert_awaited_once_with("target_jti")


async def test_logout_silently_ignores_invalid_token(auth_service, refresh_repo, token_service):
    token_service.validate_refresh_token.side_effect = ValueError("bad token")

    await auth_service.logout("invalid_token")  # must not raise

    refresh_repo.revoke_by_jti.assert_not_awaited()


# --- get_user_by_id ---

async def test_get_user_by_id_returns_wrapped_user(auth_service, user_repo):
    user = make_mock_user()
    user_repo.get_by_id.return_value = user
    user_repo.get_effective_role.return_value = "admin"

    result = await auth_service.get_user_by_id(user.id)

    assert result is not None
    assert result.id == user.id
    assert result.email == user.email
    assert result.role == "admin"


async def test_get_user_by_id_returns_none_for_missing_user(auth_service, user_repo):
    user_repo.get_by_id.return_value = None

    result = await auth_service.get_user_by_id(uuid4())

    assert result is None


# --- get_all_users ---

async def test_get_all_users_returns_dto_list(auth_service, user_repo):
    users = [make_mock_user(f"u{i}@example.com") for i in range(3)]
    user_repo.get_all.return_value = [(u, "user") for u in users]

    result = await auth_service.get_all_users()

    assert len(result) == 3
    assert all(isinstance(dto, UserInfoDto) for dto in result)


async def test_get_all_users_returns_empty_list(auth_service, user_repo):
    user_repo.get_all.return_value = []

    result = await auth_service.get_all_users()

    assert result == []


# --- set_user_role ---

async def test_set_user_role_updates_and_returns_dto(auth_service, user_repo):
    user = make_mock_user()
    user_repo.get_by_id.return_value = user

    result = await auth_service.set_user_role(user.id, UserRole.MANAGER)

    user_repo.update_role.assert_awaited_once_with(user.id, UserRole.MANAGER)
    assert result.role == UserRole.MANAGER.value
    assert isinstance(result, UserInfoDto)


async def test_set_user_role_raises_404_for_missing_user(auth_service, user_repo):
    from fastapi import HTTPException
    user_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.set_user_role(uuid4(), UserRole.ADMIN)

    assert exc_info.value.status_code == 404


# --- has_privileged_role ---

async def test_has_privileged_role_true_for_admin(auth_service, user_repo):
    user = make_mock_user()
    user_repo.get_by_email.return_value = user
    user_repo.get_effective_role.return_value = "admin"

    result = await auth_service.has_privileged_role("admin@example.com")

    assert result is True


async def test_has_privileged_role_true_for_manager(auth_service, user_repo):
    user = make_mock_user()
    user_repo.get_by_email.return_value = user
    user_repo.get_effective_role.return_value = "manager"

    result = await auth_service.has_privileged_role("manager@example.com")

    assert result is True


async def test_has_privileged_role_raises_for_plain_user(auth_service, user_repo):
    user = make_mock_user()
    user_repo.get_by_email.return_value = user
    user_repo.get_effective_role.return_value = "user"

    with pytest.raises(ValueError, match="Insufficient permissions"):
        await auth_service.has_privileged_role("user@example.com")


async def test_has_privileged_role_raises_when_user_not_found(auth_service, user_repo):
    user_repo.get_by_email.return_value = None

    with pytest.raises(ValueError, match="User not found"):
        await auth_service.has_privileged_role("ghost@example.com")
