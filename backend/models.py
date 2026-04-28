from pydantic import BaseModel # type: ignore
from typing import Optional, List
import uuid


class User(BaseModel):
    id: int
    nickname: str
    points: int
    company: Optional[str] = None
    password: str


class LoginRequest(BaseModel):
    password: str


class Event(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    points: int = 0
    date: str  # для простоты используем строку
    is_archived: bool = False

class Registration(BaseModel):
    user_id: int
    event_id: int


class EventResponse(BaseModel):
    id: int
    name: str
    tags: List[str] = []
    points: int = 0
    date: str
    is_registered: bool = False
