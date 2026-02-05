from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task
from fastapi import HTTPException, status
from sqlalchemy.future import select

class Taskservice:

    @staticmethod
    async def create_task(db: AsyncSession, user_id: int, data: TaskCreate):
        task = Task(
            title=data.title,
            description=data.description,
            user_id=user_id
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def get_user_tasks(db: AsyncSession, user_id: int):
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_task(db: AsyncSession, task_id: int, user_id: int):
        stmt = select(Task).where(Task.id == task_id,
            Task.user_id == user_id)
        result = await db.execute(stmt)
        task = result.scalars().first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task

    @staticmethod
    async def update_task(db: AsyncSession, task: Task, data: TaskUpdate):
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status

        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def delete_task(db: AsyncSession, task: Task):
        await db.delete(task)
        await db.commit()
        return True
