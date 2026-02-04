from pydantic import BaseModel, field_validator
from typing import Optional
from app.util.enum import TaskStatus
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending

    @field_validator("title")
    def title_required(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    @field_validator("title")
    def non_empty_strings(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Field cannot be an empty string")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str 
    user_id: int
    created_at: datetime    
    
    class Config:
        from_attributes = True