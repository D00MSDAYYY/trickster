# internal
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel, func, Relationship
from pydantic_visible_fields import configure_roles


class Role(Enum):
    admin = "admin"
    user = "user"
    observer = "observer"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    nickname: str
    role: Role = Field(default=Role.user)

    firstname: str
    middlename: Optional[str] = Field(default=None)
    lastname: str

    points: int = Field(default=0)
    company: str 
    password: str

    # created_at: datetime = Field(
    #     sa_column_kwargs={"server_default": func.now()}, default=None
    # )
    created_at: datetime = Field(
        default_factory= datetime.now
    )


class EventTagLink(SQLModel, table=True):
    event_id: int = Field(foreign_key="event.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    events: List["Event"] = Relationship(back_populates="tags", link_model=EventTagLink)


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    title: str
    points: int = Field(default=0)
    date: datetime

    tags: List["Tag"] = Relationship(back_populates="events", link_model=EventTagLink,)

    description: Optional[str] = Field(default=None)
    link: Optional[str] = Field(default=None)

    is_archived: bool = Field(default=False)

    # created_at: Optional[datetime] = Field(
    #     sa_column_kwargs={"server_default": func.now()}, default=None
    # )
    created_at: datetime = Field(
        default_factory= datetime.now
    )


class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    title: str
    body: Optional[str] = Field(default=None)

    # created_at: Optional[datetime] = Field(
    #     sa_column_kwargs={"server_default": func.now()}, default=None
    # )
    created_at: datetime = Field(
        default_factory= datetime.now
    )


class Registration(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    event_id: int = Field(foreign_key="event.id", primary_key=True)

    # created_at: Optional[datetime] = Field(
    #     sa_column_kwargs={"server_default": func.now()}, default=None
    # )
    created_at: datetime = Field(
        default_factory= datetime.now
    )


class Attendance(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    event_id: int = Field(foreign_key="event.id", primary_key=True)

    # created_at: Optional[datetime] = Field(
    #     sa_column_kwargs={"server_default": func.now()}, default=None
    # )
    created_at: datetime = Field(
        default_factory= datetime.now
    )
