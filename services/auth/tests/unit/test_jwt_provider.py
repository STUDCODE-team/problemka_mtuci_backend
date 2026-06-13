import pytest
import jwt
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from common_lib.config.settings import settings
from services.jwt_provider import PyJWTTokenProvider


@pytest.fixture
def provider():
    return PyJWTTokenProvider()


def test_create_and_decode_access_token(provider):
    user_id = str(uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=15)

    token = provider.create_access_token(user_id=user_id, role="user", expires_at=expires_at)

    assert isinstance(token, str)
    payload = provider.decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == "user"
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token(provider):
    user_id = str(uuid4())
    jti = uuid4()
    expires_at = datetime.now(UTC) + timedelta(days=7)

    token = provider.create_refresh_token(jti=jti, user_id=user_id, expires_at=expires_at)

    assert isinstance(token, str)
    payload = provider.decode_refresh_token(token)
    assert payload["sub"] == user_id
    assert payload["jti"] == str(jti)
    assert payload["type"] == "refresh"


def test_decode_access_token_rejects_refresh_token(provider):
    user_id = str(uuid4())
    jti = uuid4()
    expires_at = datetime.now(UTC) + timedelta(days=7)
    refresh_token = provider.create_refresh_token(
        jti=jti, user_id=user_id, expires_at=expires_at
    )

    with pytest.raises(ValueError, match="Not an access token"):
        provider.decode_access_token(refresh_token)


def test_decode_refresh_token_rejects_access_token(provider):
    user_id = str(uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=15)
    access_token = provider.create_access_token(
        user_id=user_id, role="admin", expires_at=expires_at
    )

    with pytest.raises(ValueError, match="Not a refresh token"):
        provider.decode_refresh_token(access_token)


def test_decode_and_verify_invalid_token(provider):
    with pytest.raises(ValueError, match="Invalid token"):
        provider.decode_and_verify("not.a.valid.token")


def test_decode_and_verify_expired_token(provider):
    payload = {
        "sub": str(uuid4()),
        "type": "access",
        "exp": datetime.now(UTC) - timedelta(seconds=1),
    }
    expired_token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    with pytest.raises(ValueError, match="Invalid token"):
        provider.decode_and_verify(expired_token)


def test_decode_and_verify_wrong_secret(provider):
    payload = {
        "sub": str(uuid4()),
        "type": "access",
        "exp": datetime.now(UTC) + timedelta(minutes=15),
    }
    bad_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    with pytest.raises(ValueError, match="Invalid token"):
        provider.decode_and_verify(bad_token)
