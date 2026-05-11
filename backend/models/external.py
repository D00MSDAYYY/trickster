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
    id: int | None = field(visible_to=[Role.admin], default=None)

    nickname: str | None = field(visible_to=[Role.observer], default=None)
    role: Role | None = field(visible_to=[Role.admin], default=None)

    firstname: str | None = field(visible_to=[Role.admin], default=None)
    middlename: str | None = field(visible_to=[Role.admin], default=None)
    lastname: str | None = field(visible_to=[Role.admin], default=None)

    points: int | None = field(visible_to=[Role.observer], default=None)
    company: str | None = field(visible_to=[Role.user], default=None)
    password: str | None = field(visible_to=[Role.admin], default=None)

    created_at: datetime | None = field(visible_to=[Role.admin], default=None)


class SettingsResponse(VisibleFieldsModel):
    app_theme: AppTheme | None = field(visible_to=[Role.user], default=None)

    days_to_notify: int | None = field(visible_to=[Role.user], default=None)
    do_notify: bool | None = field(visible_to=[Role.user], default=None)


class TagInfoResponse(VisibleFieldsModel):
    id: int | None = field(visible_to=[Role.admin], default=None)
    title: str | None = field(visible_to=[Role.observer], default=None)


class EventInfoResponse(VisibleFieldsModel):
    id: int | None = field(visible_to=[Role.admin], default=None)

    title: str | None = field(visible_to=[Role.observer], default=None)
    points: int | None = field(visible_to=[Role.observer], default=None)
    date: datetime | None = field(visible_to=[Role.observer], default=None)

    tags: List["TagInfoResponse"] | None = field(
        visible_to=[Role.observer], default=None
    )

    description: str | None = field(visible_to=[Role.observer], default=None)
    link: str | None = field(visible_to=[Role.observer], default=None)

    is_archived: bool | None = field(visible_to=[Role.admin], default=None)
    is_registered: bool | None = field(visible_to=[Role.user], default=None)

    created_at: datetime | None = field(visible_to=[Role.admin], default=None)


class NotificationInfoResponse(VisibleFieldsModel):
    id: int | None = field(visible_to=[Role.admin], default=None)

    title: str | None = field(visible_to=[Role.user], default=None)
    body: str | None = field(visible_to=[Role.user], default=None)

    created_at: datetime | None = field(visible_to=[Role.admin], default=None)


class LoginRequest(BaseModel):
    password: str
