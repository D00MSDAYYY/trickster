from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field  # type: ignore


class Roles(Enum):
    user = "user"
    admin = "admin"


class User(BaseModel):
    id: int
    nickname: str
    points: int
    company: Optional[str] = None
    password: str
    role: Roles = Roles.user
    notify_three_days: bool = False


class Event(BaseModel):
    id: Optional[int] = None
    name: str
    tags: List[str] = []
    points: int = 0
    date: str
    description: Optional[str] = None
    link: Optional[str] = None
    is_archived: bool = False
    is_registered: Optional[bool] = None


class Notification(BaseModel):
    id: int
    title: str
    body: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class LoginRequest(BaseModel):
    password: str


class Registration(BaseModel):
    user_id: int
    event_id: int


class Tag(BaseModel):
    id: int
    name: str


class ProfileUpdate(BaseModel):
    company: Optional[str] = None
    notify_three_days: Optional[bool] = None


class Attendance(BaseModel):
    user_id: int
    event_id: int

class UserSearchItem(BaseModel):
    id: int
    nickname: str
