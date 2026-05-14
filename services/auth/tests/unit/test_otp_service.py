import pytest
from unittest.mock import AsyncMock, patch

from common_lib.utils.crypto import hash_value
from services.otp_service import OTPService


@pytest.fixture
def otp_repo():
    repo = AsyncMock()
    repo.save = AsyncMock()
    repo.get = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def otp_service(otp_repo):
    return OTPService(otp_repository=otp_repo)


async def test_create_otp_saves_hash_and_sends_email(otp_service, otp_repo):
    with patch(
        "common_lib.clients.notification_client.send_otp_email",
        new_callable=AsyncMock,
    ) as mock_send:
        await otp_service.create_otp("user@example.com")

    otp_repo.save.assert_awaited_once()
    email_arg, hash_arg, ttl_arg = otp_repo.save.call_args[0]
    assert email_arg == "user@example.com"
    assert len(hash_arg) == 64  # SHA-256 hex digest
    assert ttl_arg == 300  # OTP_TTL_SEC default

    mock_send.assert_awaited_once()
    sent_email, sent_otp = mock_send.call_args[0]
    assert sent_email == "user@example.com"
    assert len(sent_otp) == 6
    assert sent_otp.isdigit()


async def test_verify_otp_default_code_bypasses_hash(otp_service, otp_repo):
    # GENERATE_DEFAULT_OTP=true in conftest.py → "123456" is always valid
    result = await otp_service.verify_otp("user@example.com", "123456")

    assert result is True
    otp_repo.delete.assert_awaited_once_with("user@example.com")
    otp_repo.get.assert_not_awaited()


async def test_verify_otp_returns_false_when_no_stored_otp(otp_service, otp_repo, monkeypatch):
    from common_lib.config.settings import settings
    monkeypatch.setattr(settings, "GENERATE_DEFAULT_OTP", False)
    otp_repo.get.return_value = None

    result = await otp_service.verify_otp("user@example.com", "654321")

    assert result is False
    otp_repo.delete.assert_not_awaited()


async def test_verify_otp_returns_false_on_wrong_code(otp_service, otp_repo, monkeypatch):
    from common_lib.config.settings import settings
    monkeypatch.setattr(settings, "GENERATE_DEFAULT_OTP", False)
    otp_repo.get.return_value = hash_value("123456")

    result = await otp_service.verify_otp("user@example.com", "999999")

    assert result is False
    otp_repo.delete.assert_not_awaited()


async def test_verify_otp_returns_true_on_correct_code(otp_service, otp_repo, monkeypatch):
    from common_lib.config.settings import settings
    monkeypatch.setattr(settings, "GENERATE_DEFAULT_OTP", False)
    correct_code = "789012"
    otp_repo.get.return_value = hash_value(correct_code)

    result = await otp_service.verify_otp("user@example.com", correct_code)

    assert result is True
    otp_repo.delete.assert_awaited_once_with("user@example.com")
