import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import UserORM
from src.repository import users as users_repository
from src.schemas.users import UserCreateSchema


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email_found(self):
        user = UserORM()
        self.session.scalars().first.return_value = user
        result = await users_repository.get_user_by_email(
            self.session, email="test@example.com"
        )
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.scalars().first.return_value = None
        result = await users_repository.get_user_by_email(
            self.session, email="test@example.com"
        )
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserCreateSchema(
            email="test@example.com",
            password="hashed_pw",
            first_name="John",
            last_name="Doe"
        )
        user_model = await users_repository.create_user(self.session, body)
        self.session.add.assert_called()
        self.session.commit.assert_called()
        self.session.refresh.assert_called_with(user_model)
        self.assertEqual(user_model.email, body.email)
        self.assertEqual(user_model.hashed_password, body.password)

    async def test_update_refresh_token(self):
        user = UserORM()
        self.session.scalars().first.return_value = user
        self.session.commit.return_value = None

        await users_repository.update_refresh_token(
            self.session, email="test@example.com", token="new_refresh_token"
        )
        self.assertEqual(user.refresh_token, "new_refresh_token")
        self.session.commit.assert_called()

    async def test_confirmed_email(self):
        user = UserORM()
        self.session.scalars().first.return_value = user
        self.session.commit.return_value = None

        await users_repository.confirmed_email(
            self.session, email="test@example.com"
        )
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called()

    async def test_update_avatar(self):
        user = UserORM()
        self.session.scalars().first.return_value = user
        self.session.refresh.return_value = None

        result = await users_repository.update_avatar(
            self.session, email="test@example.com", url="http://avatar.url"
        )
        self.assertEqual(user.avatar, "http://avatar.url")
        self.session.commit.assert_called()
        self.session.refresh.assert_called_with(user)
        self.assertEqual(result, user)


if __name__ == "__main__":
    unittest.main()
