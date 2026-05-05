# external
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from pydantic_visible_fields import VisibleFieldsModel, field, configure_roles
from .internal import Role

configure_roles(
    role_enum=Role,
    inheritance={
        Role.admin: [Role.user],
        Role.user: [Role.observer],
    },
    default_role=Role.observer,
)


class UserInfoResponse(VisibleFieldsModel):
    id: int | None = field(visible_to=[Role.admin])

    nickname: str = field(visible_to=[Role.observer])
    role: Role = field(visible_to=[Role.admin])

    firstname: str = field(visible_to=[Role.admin])
    middlename: Optional[str] = field(visible_to=[Role.admin])
    lastname: str = field(visible_to=[Role.admin])

    points: int = field(visible_to=[Role.observer])
    company: str = field(visible_to=[Role.user])
    password: str = field(visible_to=[Role.admin])

    created_at: datetime = field(visible_to=[Role.admin])


class TagInfoResponse(VisibleFieldsModel):
    id: int | None = field(visible_to=[Role.admin])
    name: str = field(visible_to=[Role.observer])


class EventInfoResponse(VisibleFieldsModel):
    id: int | None = field(visible_to=[Role.admin])

    title: str = field(visible_to=[Role.observer])
    points: int = field(visible_to=[Role.observer])
    date: datetime = field(visible_to=[Role.observer])

    tags: Optional[List["TagInfoResponse"]] = field(visible_to=[Role.observer])

    description: Optional[str] = field(visible_to=[Role.observer])
    link: Optional[str] = field(visible_to=[Role.observer])

    is_archived: bool = field(visible_to=[Role.admin])
    is_registered: bool = field(visible_to=[Role.user])

    created_at: datetime = field(visible_to=[Role.admin])


class NotificationInfoResponse(VisibleFieldsModel):
    id: int | None = field(visible_to=[Role.admin])

    title: str = field(visible_to=[Role.user])
    body: Optional[str] = field(visible_to=[Role.user])

    created_at: datetime = field(visible_to=[Role.admin])


class LoginRequest(BaseModel):
    password: str