from pydantic import BaseModel, EmailStr


class TokenSchema(BaseModel):
    access_token:  str
    refresh_token: str | None = None
    token_type:    str = "bearer"


class RequestEmailSchema(BaseModel):
    email: EmailStr
