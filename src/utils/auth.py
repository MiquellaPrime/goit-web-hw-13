from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from src.config import TOKEN_TYPE_FIELD
from src.settings import settings


def create_jwt(
        token_type: str,
        payload: dict[str, Any],
        expire_delta: timedelta | None = None,
) -> str:
    """
    Creates a JWT token with the specified type and optional expiration.

    :param token_type: The type of the token (e.g., "access", "refresh", "verify").
    :type token_type: str
    :param payload: The payload data to encode in the token.
    :type payload: dict[str, Any]
    :param expire_delta: Optional timedelta for custom expiration.
    :type expire_delta: timedelta | None
    :return: The encoded JWT token.
    :rtype: str
    """
    payload.update({TOKEN_TYPE_FIELD: token_type})
    return encode_jwt(payload, expire_delta)


def encode_jwt(
        payload: dict[str, Any],
        expire_delta: timedelta | None = None,
) -> str:
    """
    Encodes a payload into a JWT token with expiration and issued-at claims.

    :param payload: The payload to encode.
    :type payload: dict[str, Any]
    :param expire_delta: Optional timedelta for custom expiration.
    :type expire_delta: timedelta | None
    :return: The encoded JWT string.
    :rtype: str
    """
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_delta:
        expire = now + expire_delta
    else:
        expire = now + timedelta(minutes=settings.jwt.access_token_expire_minutes)
    to_encode.update(exp=expire, iat=now)
    encoded = jwt.encode(
        to_encode,
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm
    )
    return encoded


def decode_jwt(token: str) -> dict[str, Any]:
    """
    Decodes a JWT token and returns the payload.

    :param token: The JWT token to decode.
    :type token: str
    :return: The decoded token payload.
    :rtype: dict[str, Any]
    :raises JWTError: If the token is invalid or has expired.
    """
    decoded = jwt.decode(
        token,
        settings.jwt.secret_key,
        algorithms=[settings.jwt.algorithm],
    )
    return decoded
