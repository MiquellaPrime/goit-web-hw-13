import pickle
from datetime import timedelta
from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from redis import Redis
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext

from src.config import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    VERIFY_TOKEN_TYPE,
)
from src.settings import settings
from src.database.db import get_db
from src.database.models import UserORM
from src.database.redis import get_redis
from src.repository import users as user_repository
from src.utils import auth as auth_utils

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    :param password: The plain text password.
    :type password: str
    :return: The hashed password.
    :rtype: str
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches a hashed password.

    :param plain_password: The plain text password.
    :type plain_password: str
    :param hashed_password: The hashed password.
    :type hashed_password: str
    :return: True if the password matches, otherwise False.
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_model: UserORM) -> str:
    """
    Creates a JWT access token for a given user.

    :param user_model: The user model to generate a token for.
    :type user_model: UserORM
    :return: A JWT access token.
    :rtype: str
    """
    payload = {
        "sub": user_model.email,
    }
    return auth_utils.create_jwt(ACCESS_TOKEN_TYPE, payload)


def create_refresh_token(user_model: UserORM) -> str:
    """
    Creates a JWT refresh token for a given user.

    :param user_model: The user model to generate a token for.
    :type user_model: UserORM
    :return: A JWT refresh token.
    :rtype: str
    """
    payload = {
        "sub": user_model.email,
    }
    expire_delta = timedelta(days=settings.jwt.refresh_token_expire_days)
    return auth_utils.create_jwt(REFRESH_TOKEN_TYPE, payload, expire_delta)


def decode_refresh_token(token: str) -> str:
    """
    Decodes and validates a refresh token, returning the user's email.

    :param token: The refresh token to decode.
    :type token: str
    :return: The email of the user encoded in the token.
    :rtype: str
    :raises HTTPException: If the token is invalid or not a refresh token.
    """
    try:
        payload = auth_utils.decode_jwt(token)
        token_type = payload[TOKEN_TYPE_FIELD]
        if token_type == REFRESH_TOKEN_TYPE:
            return payload["sub"]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token type.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")


def create_verify_token(user_model: UserORM) -> str:
    """
    Creates a JWT verification token for email confirmation.

    :param user_model: The user model to generate the token for.
    :type user_model: UserORM
    :return: A JWT verification token.
    :rtype: str
    """
    payload = {
        "sub": user_model.email,
    }
    expire_delta = timedelta(days=1)
    return auth_utils.create_jwt(VERIFY_TOKEN_TYPE, payload, expire_delta)


def decode_verify_token(token: str) -> str:
    """
    Decodes and validates an email verification token.

    :param token: The verification token to decode.
    :type token: str
    :return: The email of the user encoded in the token.
    :rtype: str
    :raises HTTPException: If the token is invalid or not a verification token.
    """
    try:
        payload = auth_utils.decode_jwt(token)
        token_type = payload[TOKEN_TYPE_FIELD]
        if token_type == VERIFY_TOKEN_TYPE:
            return payload["sub"]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token type.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")


async def authenticate_user(db: Session, email: str, password: str) -> UserORM | None:
    """
    Authenticates a user by verifying email and password.

    :param db: The database session.
    :type db: Session
    :param email: The user's email.
    :type email: str
    :param password: The user's password.
    :type password: str
    :return: The authenticated user object, or None if authentication fails.
    :rtype: UserORM | None
    """
    user_model = await user_repository.get_user_by_email(db, email)
    if user_model is None:
        return None
    if not verify_password(password, user_model.hashed_password):
        return None
    return user_model


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[Session, Depends(get_db)],
        r: Annotated[Redis, Depends(get_redis)],
):
    """
    Retrieves the current user based on the access token.

    :param token: The access token from the request.
    :type token: str
    :param db: The database session.
    :type db: Session
    :param r: The Redis cache instance.
    :type r: Redis
    :return: The authenticated user object.
    :rtype: UserORM
    :raises HTTPException: If the token is invalid or user cannot be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth_utils.decode_jwt(token)
        if payload[TOKEN_TYPE_FIELD] == ACCESS_TOKEN_TYPE:
            email = payload["sub"]
            if email is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    cached_user_model = await r.get(f"user:{email}")
    if cached_user_model is None:
        user_model = await user_repository.get_user_by_email(db, email)
        if user_model is None:
            raise credentials_exception
        await r.set(f"user:{email}", pickle.dumps(user_model))
        await r.expire(f"user:{email}", 900)
    else:
        user_model = pickle.loads(cached_user_model)
    return user_model
