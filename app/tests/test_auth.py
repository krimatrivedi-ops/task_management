from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.config import settings

def test_register_user(client: TestClient, db_session: Session):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"
    assert "password_hash" not in data
    assert data["is_active"] == False

    user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.password_hash is not None


def test_register_existing_user(client: TestClient, db_session: Session):
    client.post(
        "/auth/register",
        json={"email": "existing@example.com", "password": "testpassword"}
    )
    response = client.post(
        "/auth/register",
        json={"email": "existing@example.com", "password": "anotherpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

def test_login_user(client: TestClient, db_session: Session):
    # Register a user first
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "loginpassword"}
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "loginpassword"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient, db_session: Session):
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

    # Test with correct email but wrong password
    client.post(
        "/auth/register",
        json={"email": "wrongpass@example.com", "password": "correctpassword"}
    )
    response = client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
