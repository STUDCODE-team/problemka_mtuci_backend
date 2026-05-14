import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from services.token_service import TokenService


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.create_access_token.return_value = "mock_access_token"
    provider.create_refresh_token.return_value = "mock_refresh_token"
    provider.decode_access_token.return_value = {
        "sub": str(uuid4()),
        "role": "user",
        "type": "access",
    }
    provider.decode_refresh_token.return_value = {
        "sub": str(uuid4()),
        "jti": str(uuid4()),
        "type": "refresh",
    }
    return provider


@pytest.fixture
def token_service(mock_provider):
    return TokenService(token_provider=mock_provider)


def test_create_access_token_calls_provider(token_service, mock_provider):
    user_id = str(uuid4())
    token = token_service.create_access_token(user_id=user_id, role="user")

    assert token == "mock_access_token"
    mock_provider.create_access_token.assert_called_once()
    args = mock_provider.create_access_token.call_args[0]
    assert args[0] == user_id
    assert args[1] == "user"


def test_generate_refresh_token_returns_token_and_jti(token_service, mock_provider):
    user_id = str(uuid4())
    token, jti = token_service.generate_refresh_token(user_id=user_id)

    assert token == "mock_refresh_token"
    assert isinstance(jti, str)
    # jti should be a valid UUID string
    from uuid import UUID
    UUID(jti)  # raises if not a valid UUID


def test_validate_access_token_delegates_to_provider(token_service, mock_provider):
    payload = token_service.validate_access_token("some_token")

    mock_provider.decode_access_token.assert_called_once_with("some_token")
    assert payload["type"] == "access"


def test_validate_refresh_token_delegates_to_provider(token_service, mock_provider):
    payload = token_service.validate_refresh_token("some_refresh_token")

    mock_provider.decode_refresh_token.assert_called_once_with("some_refresh_token")
    assert payload["type"] == "refresh"


def test_validate_access_token_propagates_error(token_service, mock_provider):
    mock_provider.decode_access_token.side_effect = ValueError("Invalid token")

    with pytest.raises(ValueError, match="Invalid token"):
        token_service.validate_access_token("bad_token")
