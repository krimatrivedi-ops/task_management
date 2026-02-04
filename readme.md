# Task Management API — FastAPI + JWT + SQLAlchemy + Alembic

A complete **Task Management REST API** built using **FastAPI**, featuring:

* JWT Authentication
* User Registration & Login
* Protected CRUD Operations for Tasks
* SQLAlchemy ORM
* Alembic Migrations
* Environment-Based Configuration
* Secure Password Hashing using Argon2
* Modular, scalable project structure

---

## 1. Project Overview

This project implements a **secure, production-ready backend API** for managing tasks.
Each user can:

* Register and authenticate
* Create, view, update, and delete their own tasks

The APIs are fully protected through JWT tokens, ensuring users can only access their own resources.

**Tech Stack used:**

* **FastAPI** — high-performance API framework
* **SQLite** (configurable to PostgreSQL/MySQL)
* **SQLAlchemy ORM**
* **Alembic** for migrations
* **JWT (PyJWT)** for authentication
* **Pydantic** and **pydantic-settings** for validation & config
* **Argon2** for secure password hashing

---

## 2. Setup Instructions

### **1️⃣ Clone the Repository**

```bash
git clone <repo-url>
cd task_management
```

---

### **2️⃣ Create Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### **3️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

---

### **4️⃣ Create `.env` File**

Create a `.env` file inside project root:

```
SECRET_KEY=mysupersecretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./task.db
```

---

### **5️⃣ Run Alembic Migrations**

```bash
alembic upgrade head
```

This will generate all database tables.

---

### **6️⃣ Start the FastAPI Application**

```bash
uvicorn app.main:app --reload
```

Open the interactive Swagger UI:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 3. Authentication Flow

### **Step 1 — Register**

```
POST /auth/register
```

### **Step 2 — Login**

```
POST /auth/login
```

Returns:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

### **Step 3 — Send Token in Header for All Protected Routes**

```
Authorization: Bearer <token>
```

---

## 4. API Endpoints

### **User APIs**

| Method | Endpoint         | Description                    |
| ------ | ---------------- | ------------------------------ |
| POST   | `/auth/register` | Create new user                |
| POST   | `/auth/login`    | Get JWT token                  |
| GET    | `/users/me`      | Get current authenticated user |

---

### **Task APIs (Protected)**

| Method | Endpoint      | Description       |
| ------ | ------------- | ----------------- |
| POST   | `/tasks`      | Create task       |
| GET    | `/tasks`      | List user’s tasks |
| GET    | `/tasks/{id}` | Get one task      |
| PUT    | `/tasks/{id}` | Update task       |
| DELETE | `/tasks/{id}` | Delete task       |

For POST `/tasks`
```json
{
  "title": "title1",
  "description": "description1"
}
```
For PUT `/tasks/id`
```json
{
  "title": "title",
  "description": "description2",
  "status": "completed"
}
```
Users may only access **their own** tasks.

---

## 5. How Protected APIs Work

Every protected API uses:

```python
current_user = Depends(get_current_user)
```

`get_current_user` performs:

1. Extract token from header
2. Decode JWT
3. Validate signature & expiration
4. Load the user from DB
5. Injects user into the endpoint

If token is invalid/missing → FastAPI automatically returns `401 Unauthorized`.

---

## 6. Password Hashing

The project uses **Argon2**, a modern, secure hashing algorithm recommended by OWASP.

```python
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)
```

Argon2 is resistant to GPU attacks & designed for secure authentication systems.

---

## 7. Database Layer (Sync SQLAlchemy)

We use SQLAlchemy in sync mode because it is simpler, more stable, and fits this project well.
FastAPI automatically offloads sync DB operations to a threadpool, so performance is not affected.
Async SQLAlchemy would make the setup more complex without providing real benefits for this CRUD API.
Sessions are provided through FastAPI dependencies and not created manually.
---


##  8. Key Learnings

### 🔹 FastAPI Architecture

Learned how to structure a real-world project using routers, schemas, services, and CRUD layers.

### 🔹 Dependency Injection

Used `Depends()` to cleanly inject DB sessions and authenticated users.

### 🔹 Secure Authentication

Implemented JWT tokens and password hashing with Argon2.

### 🔹 Database Migrations

Created DB schema using Alembic with proper version tracking.

### 🔹 Environment-Based Configuration

Used `pydantic-settings` to securely load secrets from `.env`.

### 🔹 Validation with Pydantic

Ensured clean request/response models through `BaseModel`.

### 🔹 Ownership & Authorization

Built a system where users access only their own tasks.
