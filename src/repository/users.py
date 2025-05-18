from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import UserORM
from src.schemas.users import UserCreateSchema


async def get_user_by_email(
        db: Session,
        email: str,
) -> UserORM | None:
    """
    Retrieves a user object by their email address.

    :param db: The database session.
    :type db: Session
    :param email: The email address to search for.
    :type email: str
    :return: The user object if found, otherwise None.
    :rtype: UserORM | None
    """
    stmt = select(UserORM).filter_by(email=email)
    return db.scalars(stmt).first()


async def create_user(
        db: Session,
        body: UserCreateSchema,
) -> UserORM:
    """
    Creates a new user in the system.

    :param db: The database session.
    :type db: Session
    :param body: The user data to create.
    :type body: UserCreateSchema
    :return: The created user object.
    :rtype: UserORM
    """
    user_model = UserORM(
        email=body.email,
        hashed_password=body.password,
        first_name=body.first_name,
        last_name=body.last_name,
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_model


async def update_refresh_token(
        db: Session,
        email: str,
        token: str,
):
    """
    Updates the refresh token for a user with the specified email.

    :param db: The database session.
    :type db: Session
    :param email: The email of the user whose token is being updated.
    :type email: str
    :param token: The new refresh token.
    :type token: str
    :return: None
    """
    user_model = await get_user_by_email(db, email)

    user_model.refresh_token = token
    db.commit()


async def confirmed_email(
        db: Session,
        email: str,
):
    """
    Marks the email of a user as confirmed.

    :param db: The database session.
    :type db: Session
    :param email: The email of the user to confirm.
    :type email: str
    :return: None
    """
    user_model = await get_user_by_email(db, email)
    user_model.confirmed = True
    db.commit()


async def update_avatar(
        db: Session,
        email: str,
        url: str,
) -> UserORM:
    """
    Updates the avatar URL of a user.

    :param db: The database session.
    :type db: Session
    :param email: The email of the user to update.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :return: The updated user object.
    :rtype: UserORM
    """
    user_model = await get_user_by_email(db, email)
    user_model.avatar = url
    db.commit()
    db.refresh(user_model)
    return user_model
