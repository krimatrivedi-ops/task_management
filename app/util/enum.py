from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
