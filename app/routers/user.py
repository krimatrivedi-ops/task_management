from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.models.user import User
from app.dependencies.auth import get_current_user
from sqlalchemy.orm import Session
from app.dependencies.db import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user