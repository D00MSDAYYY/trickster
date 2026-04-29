from pydantic import BaseModel  # type: ignore
from typing import Optional, List


class UserResponse(BaseModel):
    nickname: str
    points: int
    company: Optional[str] = None
    role: str = "user"  

class EventResponse(BaseModel):
    id: int
    name: str
    tags: List[str] = []
    points: int = 0
    date: str
    is_registered: bool = False


class EventDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    points: int = 0
    date: str
    is_registered: bool = False
    link: Optional[str] = None    


class NotificationResponse(BaseModel):
    id: int
    title: str
    body: Optional[str] = None
    created_at: str
