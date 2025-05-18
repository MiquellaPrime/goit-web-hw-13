from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.database.models import ContactORM
from src.schemas.contacts import (
    ContactCreateSchema,
    ContactUpdateSchema,
    ContactBirthDateUpdateSchema,
)
from src.schemas.filters import FilterParams


async def get_contacts(
        db: Session,
        user_id: int,
        fp: FilterParams
) -> list[ContactORM]:
    """
    Retrieves a list of contacts for a specific user with optional filtering.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user whose contacts to retrieve.
    :type user_id: int
    :param fp: Optional filter parameters to narrow down results.
    :type fp: FilterParams
    :return: A list of contact objects.
    :rtype: list[ContactORM]
    """
    stmt = select(ContactORM).filter_by(user_id=user_id)

    if fp.first_name:
        stmt = stmt.filter_by(first_name=fp.first_name)
    if fp.last_name:
        stmt = stmt.filter_by(last_name=fp.last_name)
    if fp.email:
        stmt = stmt.filter_by(email=fp.email)
    if fp.phone:
        stmt = stmt.filter_by(phone=fp.phone)

    return db.scalars(stmt).all()


async def get_contact_by_id(
        db: Session,
        user_id: int,
        contact_id: int
) -> ContactORM | None:
    """
    Retrieves a specific contact by its ID for a given user.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user who owns the contact.
    :type user_id: int
    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :return: The contact object if found, otherwise None.
    :rtype: ContactORM | None
    """
    stmt = select(ContactORM).filter_by(id=contact_id, user_id=user_id)
    return db.execute(stmt).first()


async def get_upcoming_birthdays(
        db: Session,
        user_id: int,
        date_list: list[str]
) -> list[ContactORM]:
    """
    Retrieves contacts whose birthdays fall on the upcoming dates.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user to search contacts for.
    :type user_id: int
    :param date_list: List of date strings (formatted as MM-DD) to match birthdays against.
    :type date_list: list[str]
    :return: A list of matching contact objects.
    :rtype: list[ContactORM]
    """
    stmt = select(ContactORM).where(
        ContactORM.user_id == user_id,
        func.to_char(ContactORM.birth_date, "MM-DD").in_(date_list)
    )
    return db.scalars(stmt).all()


async def create_contact(
        db: Session,
        user_id: int,
        body: ContactCreateSchema
):
    """
    Creates a new contact for a specific user.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user creating the contact.
    :type user_id: int
    :param body: The contact data to create.
    :type body: ContactCreateSchema
    :return: None
    """
    contact_model = ContactORM(
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        email=body.email,
        birth_date=body.birth_date,
        extra=body.extra,
        user_id=user_id
    )
    db.add(contact_model)
    db.commit()


async def update_contact(
        db: Session,
        user_id: int,
        contact_id: int,
        body: ContactUpdateSchema
) -> ContactORM | None:
    """
    Updates an existing contact's details.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user who owns the contact.
    :type user_id: int
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated contact data.
    :type body: ContactUpdateSchema
    :return: The updated contact object, or None if not found.
    :rtype: ContactORM | None
    """
    stmt = select(ContactORM).filter_by(id=contact_id, user_id=user_id)
    contact_model = db.execute(stmt).scalar()

    if contact_model is not None:
        contact_model.first_name = body.first_name
        contact_model.last_name = body.last_name
        contact_model.email = body.email
        contact_model.phone = body.phone
        contact_model.birth_date = body.birth_date
        contact_model.extra = body.extra
        db.commit()

    return contact_model


async def update_birth_date(
        db: Session,
        user_id: int,
        contact_id: int,
        body: ContactBirthDateUpdateSchema
) -> ContactORM | None:
    """
    Updates the birth date of a specific contact.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user who owns the contact.
    :type user_id: int
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated birth date.
    :type body: ContactBirthDateUpdateSchema
    :return: The updated contact object, or None if not found.
    :rtype: ContactORM | None
    """
    stmt = select(ContactORM).filter_by(id=contact_id, user_id=user_id)
    contact_model = db.execute(stmt).scalar()

    if contact_model is not None:
        contact_model.birth_date = body.birth_date
        db.commit()

    return contact_model


async def delete_contact(
        db: Session,
        user_id: int,
        contact_id: int
) -> ContactORM | None:
    """
    Deletes a specific contact by ID for a given user.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user who owns the contact.
    :type user_id: int
    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :return: The deleted contact object, or None if not found.
    :rtype: ContactORM | None
    """
    stmt = select(ContactORM).filter_by(id=contact_id, user_id=user_id)
    contact_model = db.execute(stmt).scalar()

    if contact_model is not None:
        db.delete(contact_model)
        db.commit()

    return contact_model
