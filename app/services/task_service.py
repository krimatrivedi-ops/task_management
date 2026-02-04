from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task
from fastapi import HTTPException, status

class Taskservice:

    @staticmethod
    def create_task(db: Session, user_id: int, data: TaskCreate):
        task = Task(
            title=data.title,
            description=data.description,
            user_id=user_id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def get_user_tasks(db: Session, user_id: int):
        return db.query(Task).filter(Task.user_id == user_id).order_by(Task.created_at.desc()).all()
    
    @staticmethod
    def get_task(db: Session, task_id: int, user_id: int):
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task

    @staticmethod
    def update_task(db: Session, task: Task, data: TaskUpdate):
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status

        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete_task(db: Session, task: Task):
        db.delete(task)
        db.commit()
        return True
