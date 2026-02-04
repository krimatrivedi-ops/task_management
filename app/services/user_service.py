from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from app.util.util import safe_db
from app.models.user import User
from app.schemas.user import UserCreate

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

class UserService:
    @staticmethod
    def hash_password(password: str):
        password = password.encode("utf-8")[:72].decode("utf-8")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str):
        plain = plain.encode("utf-8")[:72].decode("utf-8")
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def create_user(db: Session, data: UserCreate):
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

        user = User(
            email=data.email,
            password_hash=UserService.hash_password(data.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
        
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not UserService.verify_password(password, user.password_hash):
            return None
        return user
