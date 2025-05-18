import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import ContactORM, UserORM
from src.repository import contacts as contacts_repository
from src.schemas.contacts import (
    ContactSchema,
    ContactCreateSchema,
    ContactUpdateSchema,
    ContactBirthDateUpdateSchema
)
from src.schemas.filters import FilterParams


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user_model = UserORM(id=1)

    async def test_get_contacts(self):
        contact_models = [ContactORM(), ContactORM(), ContactORM()]
        self.session.scalars().all.return_value = contact_models
        result = await contacts_repository.get_contacts(
            self.session, self.user_model.id, FilterParams()
        )
        self.assertEqual(result, contact_models)

    async def test_get_contact_by_id_found(self):
        contact = ContactORM()
        self.session.execute().first.return_value = contact
        result = await contacts_repository.get_contact_by_id(
            self.session, self.user_model.id, contact_id=1
        )
        self.assertEqual(result, contact)

    async def test_get_contact_by_id_not_found(self):
        self.session.execute().first.return_value = None
        result = await contacts_repository.get_contact_by_id(
            self.session, self.user_model.id, contact_id=1
        )
        self.assertIsNone(result)

    async def test_get_upcoming_birthdays(self):
        contacts = [ContactORM(), ContactORM()]
        self.session.scalars().all.return_value = contacts
        result = await contacts_repository.get_upcoming_birthdays(
            self.session, self.user_model.id, date_list=["05-18", "05-19"]
        )
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactCreateSchema(
            first_name="John", last_name="Doe", phone="123456789",
            email="john@example.com", birth_date=None, extra="Note"
        )
        self.session.commit.return_value = None
        result = await contacts_repository.create_contact(
            self.session, self.user_model.id, body
        )
        self.session.add.assert_called()
        self.session.commit.assert_called()
        self.assertIsNone(result)  # бо create_contact нічого не повертає

    async def test_update_contact_found(self):
        contact = ContactORM()
        self.session.execute().scalar.return_value = contact
        self.session.commit.return_value = None
        body = ContactUpdateSchema(
            first_name="Jane", last_name="Smith", phone="987654321",
            email="jane@example.com", birth_date=None, extra="Updated"
        )
        result = await contacts_repository.update_contact(
            self.session, self.user_model.id, contact_id=1, body=body
        )
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        self.session.execute().scalar.return_value = None
        body = ContactUpdateSchema(
            first_name="Jane", last_name="Smith", phone="987654321",
            email="jane@example.com", birth_date=None, extra="Updated"
        )
        result = await contacts_repository.update_contact(
            self.session, self.user_model.id, contact_id=1, body=body
        )
        self.assertIsNone(result)

    async def test_update_birth_date_found(self):
        contact = ContactORM()
        self.session.execute().scalar.return_value = contact
        self.session.commit.return_value = None
        body = ContactBirthDateUpdateSchema(birth_date="2000-01-01")
        result = await contacts_repository.update_birth_date(
            self.session, self.user_model.id, contact_id=1, body=body
        )
        self.assertEqual(result, contact)

    async def test_update_birth_date_not_found(self):
        self.session.execute().scalar.return_value = None
        body = ContactBirthDateUpdateSchema(birth_date="2000-01-01")
        result = await contacts_repository.update_birth_date(
            self.session, self.user_model.id, contact_id=1, body=body
        )
        self.assertIsNone(result)

    async def test_delete_contact_found(self):
        contact = ContactORM()
        self.session.execute().scalar.return_value = contact
        self.session.commit.return_value = None
        result = await contacts_repository.delete_contact(
            self.session, self.user_model.id, contact_id=1
        )
        self.session.delete.assert_called_with(contact)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        self.session.execute().scalar.return_value = None
        result = await contacts_repository.delete_contact(
            self.session, self.user_model.id, contact_id=1
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
