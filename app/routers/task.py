from fastapi import APIRouter, Depends
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.services.task_service import Taskservice

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await Taskservice.create_task(db, current_user.id, data)

@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await Taskservice.get_user_tasks(db, current_user.id)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await Taskservice.get_task(db, task_id, current_user.id)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = await Taskservice.get_task(db, task_id, current_user.id)
    return await Taskservice.update_task(db, task, data)

@router.delete("/{task_id}")    
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = await Taskservice.get_task(db, task_id, current_user.id)
    await Taskservice.delete_task(db, task)
    return {"message": "Task deleted successfully"}