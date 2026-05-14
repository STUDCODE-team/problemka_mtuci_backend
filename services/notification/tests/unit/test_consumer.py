import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from messaging.consumer import _handle, _on_message


# --- _handle ---

async def test_handle_otp_email_calls_send_otp_email():
    with patch(
        "messaging.consumer.send_otp_email", new_callable=AsyncMock
    ) as mock_send:
        await _handle({"type": "otp_email", "to_email": "user@example.com", "otp": "123456"})

    mock_send.assert_awaited_once_with(to_email="user@example.com", otp="123456")


async def test_handle_push_creates_push_service_and_sends():
    user_id = str(uuid4())
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_push_service = AsyncMock()

    with (
        patch("messaging.consumer.AsyncSessionLocal", return_value=mock_session),
        patch("messaging.consumer.PushService", return_value=mock_push_service),
    ):
        await _handle({
            "type": "push",
            "user_id": user_id,
            "title": "Test Title",
            "body": "Test Body",
            "data": {"key": "value"},
        })

    mock_push_service.send_push_to_user.assert_awaited_once()
    call_kwargs = mock_push_service.send_push_to_user.call_args[1]
    assert str(call_kwargs["user_id"]) == user_id
    assert call_kwargs["title"] == "Test Title"
    assert call_kwargs["body"] == "Test Body"


async def test_handle_push_passes_none_data_when_missing():
    user_id = str(uuid4())
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_push_service = AsyncMock()

    with (
        patch("messaging.consumer.AsyncSessionLocal", return_value=mock_session),
        patch("messaging.consumer.PushService", return_value=mock_push_service),
    ):
        await _handle({
            "type": "push",
            "user_id": user_id,
            "title": "T",
            "body": "B",
        })

    call_kwargs = mock_push_service.send_push_to_user.call_args[1]
    assert call_kwargs["data"] is None


async def test_handle_unknown_type_does_not_raise():
    # Should log a warning but not raise
    await _handle({"type": "totally_unknown", "data": "whatever"})


# --- _on_message ---

async def test_on_message_acks_on_success():
    message = MagicMock()
    message.body = json.dumps({"type": "otp_email", "to_email": "a@b.com", "otp": "111111"}).encode()
    message.ack = AsyncMock()
    message.nack = AsyncMock()

    with patch("messaging.consumer._handle", new=AsyncMock()):
        await _on_message(message)

    message.ack.assert_awaited_once()
    message.nack.assert_not_awaited()


async def test_on_message_nacks_on_exception():
    message = MagicMock()
    message.body = b'{"type": "otp_email"}'
    message.ack = AsyncMock()
    message.nack = AsyncMock()

    with patch("messaging.consumer._handle", new=AsyncMock(side_effect=RuntimeError("boom"))):
        await _on_message(message)

    message.nack.assert_awaited_once_with(requeue=False)
    message.ack.assert_not_awaited()
