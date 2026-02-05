from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.future import select

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
    async def create_user(db: AsyncSession, data: UserCreate):
        stmt = select(User).where(User.email == data.email)
        result = await db.execute(stmt)
        existing = result.scalars().first()
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
        await db.commit()
        await db.refresh(user)
        return user
        
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if not user:
            return None
        if not UserService.verify_password(password, user.password_hash):
            return None
        return user
