# external
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from pydantic_visible_fields import VisibleFieldsModel, field, configure_roles
from .internal import Role, AppTheme

configure_roles(
    role_enum=Role,
    inheritance={
        Role.admin: [Role.user],
        Role.user: [Role.observer],
    },
    default_role=Role.observer,
)


class UserInfoResponse(VisibleFieldsModel):
    id: Optional[int] = field(visible_to=[Role.admin], default=None)

    nickname: Optional[str] = field(visible_to=[Role.observer], default=None)
    role: Optional[Role] = field(visible_to=[Role.admin], default=None)

    firstname: Optional[str] = field(visible_to=[Role.admin], default=None)
    middlename: Optional[str] = field(visible_to=[Role.admin], default=None)
    lastname: Optional[str] = field(visible_to=[Role.admin], default=None)

    points: Optional[int] = field(visible_to=[Role.observer], default=None)
    company: Optional[str] = field(visible_to=[Role.user], default=None)
    password: Optional[str] = field(visible_to=[Role.admin], default=None)

    created_at: Optional[datetime] = field(visible_to=[Role.admin], default=None)


class SettingsResponse(VisibleFieldsModel):
    app_theme: AppTheme = field(visible_to=[Role.user])

    days_to_notify: int = field(visible_to=[Role.user])
    do_notify: bool = field(visible_to=[Role.user])


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
