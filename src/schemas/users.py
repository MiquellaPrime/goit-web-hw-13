from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBaseSchema(BaseModel):
    email:      EmailStr
    first_name: str
    last_name:  str | None = None


class UserSchema(UserBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    avatar: str | None = None
    created_at: datetime | None = None


class UserCreateSchema(UserBaseSchema):
    password: str
