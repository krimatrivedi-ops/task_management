from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.routers.auth import create_access_token

def get_auth_token(client: TestClient, email: str, password: str):
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_read_users_me_authenticated(client: TestClient, db_session: Session):
    email = "me@example.com"
    password = "testpassword"
    token = get_auth_token(client, email, password)

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert "password_hash" not in data


def test_read_users_me_unauthenticated(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

