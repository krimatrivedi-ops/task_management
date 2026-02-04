from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.user import User
from app.util.enum import TaskStatus

def get_auth_token(client: TestClient, email: str, password: str):
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]

def test_create_task(client: TestClient, db_session: Session):
    token = get_auth_token(client, "taskuser@example.com", "testpassword")
    
    response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Task", "description": "This is a test description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test description"
    assert data["status"] == TaskStatus.pending.value
    assert "id" in data
    assert "user_id" in data

    task = db_session.query(Task).filter(Task.id == data["id"]).first()
    assert task is not None
    assert task.title == "Test Task"

def test_create_task_unauthenticated(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Unauthorized Task", "description": "Should not be created"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_list_tasks(client: TestClient, db_session: Session):
    # User 1
    token1 = get_auth_token(client, "user1@example.com", "testpassword")
    client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "User1 Task 1", "description": "Desc 1"}
    )
    client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "User1 Task 2", "description": "Desc 2"}
    )

    # User 2
    token2 = get_auth_token(client, "user2@example.com", "testpassword")
    client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token2}"},
        json={"title": "User2 Task 1", "description": "Desc 3"}
    )

    response1 = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1) == 2
    assert any(task["title"] == "User1 Task 1" for task in data1)
    assert any(task["title"] == "User1 Task 2" for task in data1)

    response2 = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) == 1
    assert any(task["title"] == "User2 Task 1" for task in data2)

def test_get_single_task(client: TestClient, db_session: Session):
    user_email = "singletask@example.com"
    token = get_auth_token(client, user_email, "testpassword")

    # Create a task for this user
    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Single Task", "description": "Description for single task"}
    )
    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Single Task"

def test_get_single_task_not_found(client: TestClient, db_session: Session):
    token = get_auth_token(client, "notfound@example.com", "testpassword")
    response = client.get(
        "/tasks/9999", # Non-existent task ID
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_get_single_task_other_user(client: TestClient, db_session: Session):
    # User 1 creates a task
    token1 = get_auth_token(client, "owner@example.com", "testpassword")
    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "Owner's Task", "description": "Only owner can see"}
    )
    task_id = create_response.json()["id"]

    # User 2 tries to access User 1's task
    token2 = get_auth_token(client, "intruder@example.com", "testpassword")
    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404 # Should be 404 because it's not found for this user
    assert response.json()["detail"] == "Task not found"


def test_update_task(client: TestClient, db_session: Session):
    user_email = "updatetask@example.com"
    token = get_auth_token(client, user_email, "testpassword")

    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Old Title", "description": "Old Description"}
    )
    task_id = create_response.json()["id"]

    update_payload = {
        "title": "New Title",
        "description": "New Description",
        "status": TaskStatus.completed.value
    }
    response = client.put(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "New Title"
    assert data["description"] == "New Description"
    assert data["status"] == TaskStatus.completed.value

    # Verify in DB
    updated_task = db_session.query(Task).filter(Task.id == task_id).first()
    assert updated_task.title == "New Title"
    assert updated_task.description == "New Description"
    assert updated_task.status == TaskStatus.completed.value

def test_update_task_other_user(client: TestClient, db_session: Session):
    # User 1 creates a task
    token1 = get_auth_token(client, "updateowner@example.com", "testpassword")
    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "Owner's Task to Update", "description": "Only owner can update"}
    )
    task_id = create_response.json()["id"]

    # User 2 tries to update User 1's task
    token2 = get_auth_token(client, "updateintruder@example.com", "testpassword")
    update_payload = {"title": "Malicious Update"}
    response = client.put(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json=update_payload
    )
    assert response.status_code == 404 # Should be 404 because task not found for this user
    assert response.json()["detail"] == "Task not found"

def test_delete_task(client: TestClient, db_session: Session):
    user_email = "deletetask@example.com"
    token = get_auth_token(client, user_email, "testpassword")

    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Task to Delete", "description": "This will be deleted"}
    )
    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

    # Verify in DB
    deleted_task = db_session.query(Task).filter(Task.id == task_id).first()
    assert deleted_task is None

def test_delete_task_other_user(client: TestClient, db_session: Session):
    # User 1 creates a task
    token1 = get_auth_token(client, "deleteowner@example.com", "testpassword")
    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "Owner's Task to Delete", "description": "Only owner can delete"}
    )
    task_id = create_response.json()["id"]

    # User 2 tries to delete User 1's task
    token2 = get_auth_token(client, "deleteintruder@example.com", "testpassword")
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404 # Should be 404 because task not found for this user
    assert response.json()["detail"] == "Task not found"

