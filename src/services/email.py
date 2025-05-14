from pathlib import Path

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from fastapi_mail.connection import ConnectionErrors

from src.database.models import UserORM
from src.services import auth as auth_service
from src.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail.user,
    MAIL_PASSWORD=settings.mail.passwd,
    MAIL_FROM=settings.mail.user,
    MAIL_PORT=settings.mail.port,
    MAIL_SERVER=settings.mail.server,
    MAIL_FROM_NAME="AddressBook App Support",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(user_model: UserORM, host: str):
    try:
        verification_token = auth_service.create_verify_token(user_model)
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[user_model.email],
            template_body={
                "host": host,
                "username": f"{user_model.first_name} {user_model.last_name}",
                "token": verification_token
            },
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as e:
        print(e)
