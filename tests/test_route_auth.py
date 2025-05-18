import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import UserORM


def test_signup_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)

    response = client.post("/auth/signup", json=user)
    assert response.status_code == 201, response.text


def test_signup_user_conflict(client, user):
    response = client.post("/auth/signup", json=user)
    assert response.status_code == 409
    assert response.json()["detail"] == "Account already exists."


def test_login_not_confirmed(client, user):
    response = client.post(
        "/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email not confirmed."


def test_login_confirmed_user(client, session: Session, user):
    user_model: UserORM = session.query(UserORM).filter_by(email=user["email"]).first()
    user_model.confirmed = True
    session.commit()

    response = client.post(
        "/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client, user):
    response = client.post(
        "/auth/login",
        data={"username": user["email"], "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password."


def test_login_wrong_email(client, user):
    response = client.post(
        "/auth/login",
        data={"username": "notexist@example.com", "password": user["password"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password."


def test_request_verify_email(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)

    response = client.post("/auth/verify_email", json={"email": user["email"]})
    assert response.status_code == 200
    assert "message" in response.json()


def test_request_verify_email_already_confirmed(client, session, user):
    user_model = session.query(UserORM).filter_by(email=user["email"]).first()
    user_model.confirmed = True
    session.commit()

    response = client.post("/auth/verify_email", json={"email": user["email"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Your email is already confirmed."
