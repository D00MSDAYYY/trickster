import uuid
from typing import List
from datetime import date
from contextlib import asynccontextmanager

import redis
import uvicorn
from sqlmodel import Session, select, func
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Response, Request, Depends, Cookie
from pydantic_visible_fields import visible_fields_response

from models.internal import *
from models.external import *
from dbs import init_db, get_session
from report_generator import generate_excel_report

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
SESSION_TTL = 60 * 60 * 24  # 24 часа


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client.ping()
    init_db()
    yield


app = FastAPI(title="Event Manager API", version="0.4.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_session(session_id: str, user_id: int):
    redis_client.setex(session_id, SESSION_TTL, user_id)


def load_user_id(session_id: str) -> int | None:
    uid = redis_client.get(session_id)
    return int(uid) if uid is not None else None  # type: ignore


def delete_session(session_id: str):
    redis_client.delete(session_id)


def get_current_user(
    session_id: str | None = Cookie(None, alias="session_id"),
    session: Session = Depends(get_session),
) -> User:
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = redis_client.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def ensure_admin(user: User = Depends(get_current_user)):
    if user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )


# ---------------------------------------------------------------------------
# Аутентификация
# ---------------------------------------------------------------------------


@app.post("/login", response_model=UserInfoResponse)
async def login(
    login_data: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(User).where(User.password == login_data.password)
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    session_id = uuid.uuid4().hex
    save_session(session_id, user.id)  # type: ignore # <-- Redis
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=SESSION_TTL,
    )
    return visible_fields_response(user, role=user.role)


@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)
    response.delete_cookie("session_id")
    return {"message": "Вы вышли"}


# ---------------------------------------------------------------------------
# Профиль
# ---------------------------------------------------------------------------
@app.get("/profile", response_model=UserInfoResponse)
async def get_profile(
    user: User = Depends(get_current_user),
):
    return visible_fields_response(user, role=user.role)


@app.patch("/profile", response_model=UserInfoResponse)
async def update_profile(
    profile_data: UserInfoResponse,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    data = profile_data.model_dump(
        exclude_unset=True,
        exclude={"id", "role", "created_at"},
    )
    for field, value in data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return visible_fields_response(user, role=user.role)


# ---------------------------------------------------------------------------
# События (пользовательская часть)
# ---------------------------------------------------------------------------
def event_to_response(
    event: Event,
    role: Role,
    user_id: int | None = None,
    session: Session | None = None,
) -> EventInfoResponse:
    """Формирует EventInfoResponse с тегами и флагом регистрации."""
    data = visible_fields_response(event, role=role)

    # Получаем теги через связи
    tags = []
    if session:
        statement = (
            select(Tag).join(EventTagLink).where(EventTagLink.event_id == event.id)
        )
        tags = session.exec(statement).all()

    tag_responses = [
        TagInfoResponse(**visible_fields_response(t, role=role).model_dump())
        for t in tags
    ]

    update_dict = data.model_dump()
    update_dict["tags"] = tag_responses

    # Проверяем регистрацию
    if user_id and session:
        registration = session.exec(
            select(Registration).where(
                Registration.user_id == user_id,
                Registration.event_id == event.id,
            )
        ).first()
        update_dict["is_registered"] = registration is not None

    return EventInfoResponse(**update_dict)


@app.get("/events", response_model=List[EventInfoResponse])
async def get_events(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    statement = select(Event).where(Event.is_archived == False)
    events = session.exec(statement).all()

    return [event_to_response(e, user.role, user.id, session) for e in events]


@app.get("/events/{event_id}", response_model=EventInfoResponse)
async def get_event_detail(
    event_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return event_to_response(event, user.role, user.id, session)


@app.post("/events/{event_id}/register")
async def register_for_event(
    event_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    if event.is_archived:
        raise HTTPException(
            status_code=400, detail="Нельзя зарегистрироваться на прошедшее событие"
        )

    # Проверяем существующую регистрацию
    existing = session.exec(
        select(Registration).where(
            Registration.user_id == user.id,
            Registration.event_id == event_id,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Вы уже зарегистрированы")

    registration = Registration(user_id=user.id, event_id=event_id)  # type: ignore
    session.add(registration)
    session.commit()

    return {"message": f"Вы зарегистрированы на событие '{event.title}'"}


@app.delete("/events/{event_id}/register")
async def unregister_from_event(
    event_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    registration = session.exec(
        select(Registration).where(
            Registration.user_id == user.id,
            Registration.event_id == event_id,
        )
    ).first()

    if not registration:
        raise HTTPException(status_code=404, detail="Регистрация не найдена")

    session.delete(registration)
    session.commit()

    return {"message": f"Регистрация на '{event.title}' отменена"}


# ---------------------------------------------------------------------------
# Теги
# ---------------------------------------------------------------------------
@app.get("/tags", response_model=List[TagInfoResponse])
async def get_tags(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    tags = session.exec(select(Tag)).all()
    return [visible_fields_response(t, role=user.role) for t in tags]


# ---------------------------------------------------------------------------
# Уведомления
# ---------------------------------------------------------------------------
@app.get("/notifications", response_model=List[NotificationInfoResponse])
async def get_notifications(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    notifications = session.exec(select(Notification)).all()
    return [visible_fields_response(n, role=user.role) for n in notifications]


# ----------------------------------------------
# Настройки
# ----------------------------------------------
@app.get("/settings", response_model=SettingsResponse)
def get_settings(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not (user_settings := session.get(UserSettingsLink, user.id)):
        user_settings = UserSettingsLink(user_id=user.id)  # type: ignore
        session.add(user_settings)
        session.commit()
        session.refresh(user_settings)

    # Защита от незаполненного JSON
    if not user_settings.settings:
        user_settings.settings = Settings().model_dump(mode="json")
        session.add(user_settings)
        session.commit()
        session.refresh(user_settings)

    settings_obj = Settings(**user_settings.settings)
    return visible_fields_response(settings_obj, role=user.role).model_dump()


@app.patch("/settings", response_model=SettingsResponse)
def update_settings(
    new_settings: SettingsResponse,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not (user_settings := session.get(UserSettingsLink, user.id)):
        user_settings = UserSettingsLink(user_id=user.id)  # type: ignore
        session.add(user_settings)
        session.commit()
        session.refresh(user_settings)

    if not user_settings.settings:
        user_settings.settings = Settings().model_dump(mode="json")

    # Явное обновление словаря
    updated_dict = {
        **user_settings.settings,
        **new_settings.model_dump(exclude_unset=True),
    }
    validated = Settings(**updated_dict)
    user_settings.settings = validated.model_dump(
        mode="json"
    )  # присвоение, а не .update()

    session.add(user_settings)
    session.commit()
    session.refresh(user_settings)

    final_settings = Settings(**user_settings.settings)
    return visible_fields_response(final_settings, role=user.role).model_dump()


# ---------------------------------------------------------------------------
# Административные эндпоинты
# ---------------------------------------------------------------------------
@app.get("/admin/events", response_model=List[EventInfoResponse])
async def get_admin_events(
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    events = session.exec(select(Event)).all()
    return [event_to_response(e, Role.admin, session=session) for e in events]


@app.post("/admin/events", response_model=EventInfoResponse)
async def create_event(
    event_data: EventInfoResponse,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    # Создаём событие
    event_dict = event_data.model_dump(exclude={"tags"})
    event = Event(**event_dict)
    session.add(event)
    session.flush()

    # Обрабатываем теги
    for tag_response in event_data.tags:  # type: ignore
        tag_name = tag_response.title
        # Ищем существующий тег или создаём новый
        tag = session.exec(select(Tag).where(Tag.title == tag_name)).first()

        if not tag:
            tag = Tag(title=tag_name)  # type: ignore
            session.add(tag)
            session.flush()

        # Создаём связь
        event_tag = EventTagLink(event_id=event.id, tag_id=tag.id)  # type: ignore
        session.add(event_tag)

    session.commit()
    session.refresh(event)

    return event_to_response(event, Role.admin, session=session)


@app.patch("/admin/events/{event_id}", response_model=EventInfoResponse)
async def update_event(
    event_id: int,
    event_data: EventInfoResponse,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    update_dict = event_data.model_dump(exclude_unset=True, exclude={"tags"})

    for field, value in update_dict.items():
        if hasattr(event, field):
            setattr(event, field, value)

    # Обновляем теги, если переданы
    if event_data.tags is not None:
        # Удаляем старые связи
        old_links = session.exec(
            select(EventTagLink).where(EventTagLink.event_id == event_id)
        ).all()
        for link in old_links:
            session.delete(link)

        # Добавляем новые
        for tag_response in event_data.tags:
            tag_name = tag_response.title
            tag = session.exec(select(Tag).where(Tag.title == tag_name)).first()

            if not tag:
                tag = Tag(title=tag_name)  # type: ignore
                session.add(tag)
                session.flush()

            event_tag = EventTagLink(event_id=event.id, tag_id=tag.id)  # type: ignore
            session.add(event_tag)

    session.add(event)
    session.commit()
    session.refresh(event)

    return event_to_response(event, Role.admin, session=session)


@app.delete("/admin/events/{event_id}")
async def delete_event(
    event_id: int,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    session.delete(event)
    session.commit()
    return {"message": f"Событие удалено"}


@app.get("/admin/users/search", response_model=List[UserInfoResponse])
async def search_users(
    q: str,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    if not q or len(q.strip()) < 2:
        return []

    search_term = f"%{q.strip().lower()}%"
    statement = (
        select(User).where(func.lower(User.nickname).like(search_term)).limit(20)
    )

    users = session.exec(statement).all()

    return [visible_fields_response(u, role=admin.role) for u in users]


# ---------------------------------------------------------------------------
# Посетители мероприятия (административная часть)
# ---------------------------------------------------------------------------
@app.get("/admin/events/{event_id}/attendants", response_model=List[UserInfoResponse])
async def get_event_attendants(
    event_id: int,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    attendant_ids = session.exec(
        select(Attendance.user_id).where(Attendance.event_id == event_id)
    ).all()

    if not attendant_ids:
        return []

    statement = select(User).where(
        User.id.in_(attendant_ids)  # type: ignore[attr-defined]
    )
    users = session.exec(statement).all()
    return [visible_fields_response(u, role=admin.role) for u in users]


@app.patch("/admin/events/{event_id}/attendants")
async def update_event_attendants(
    event_id: int,
    attendant_ids: List[int],
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    old_attendants = session.exec(
        select(Attendance).where(Attendance.event_id == event_id)
    ).all()
    for att in old_attendants:
        session.delete(att)

    for uid in attendant_ids:
        session.add(Attendance(user_id=uid, event_id=event_id))

    session.commit()
    return {"message": "Список посетителей обновлён"}


@app.get("/admin/report", response_class=Response)
def generate_report(
    date_from: date,
    date_to: date,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    excel_file = generate_excel_report(session, date_from, date_to)
    filename = f"report_{date_from}_{date_to}.xlsx"
    content = excel_file.getvalue()

    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Управление пользователями (административная часть)
# ---------------------------------------------------------------------------
@app.get("/admin/users", response_model=List[UserInfoResponse])
async def get_all_users(
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    users = session.exec(select(User)).all()
    return [visible_fields_response(u, role=admin.role) for u in users]


@app.post("/admin/users", response_model=UserInfoResponse)
async def create_user(
    user_data: UserInfoResponse,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    # Проверяем, что никнейм уникален
    existing = session.exec(
        select(User).where(User.nickname == user_data.nickname)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким никнеймом уже существует"
        )

    # Создаём пользователя
    new_user = User(
        **user_data.model_dump(
            exclude_unset=True,
            exclude={"id", "role", "created_at"},
        )
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return visible_fields_response(new_user, role=admin.role)


@app.patch("/admin/users/{user_id}", response_model=UserInfoResponse)
async def update_user(
    user_id: int,
    user_data: UserInfoResponse,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем только переданные поля
    update_dict = user_data.model_dump(exclude_unset=True, exclude={"id", "created_at"})

    # Проверяем уникальность никнейма, если он меняется
    if "nickname" in update_dict and update_dict["nickname"] != user.nickname:
        existing = session.exec(
            select(User).where(User.nickname == update_dict["nickname"])
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="Пользователь с таким никнеймом уже существует"
            )

    for field, value in update_dict.items():
        if field == "role" and value:
            setattr(user, field, Role(value))
        elif field == "password" and not value:
            continue  # пустой пароль — не меняем
        elif hasattr(user, field):
            setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return visible_fields_response(user, role=admin.role)


import logging

logger = logging.getLogger("uvicorn.error")


@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(ensure_admin),
    session: Session = Depends(get_session),
):    
    user = session.get(User, user_id)
    if not user:
        logger.warning(f"Пользователь {user_id} не найден")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Удаляем связанные записи
    registrations = session.exec(
        select(Registration).where(Registration.user_id == user_id)
    ).all()
    for reg in registrations:
        session.delete(reg)

    attendances = session.exec(
        select(Attendance).where(Attendance.user_id == user_id)
    ).all()
    for att in attendances:
        session.delete(att)

    user_settings = session.get(UserSettingsLink, user_id)
    if user_settings:
        session.delete(user_settings)

    session.delete(user)
    session.commit()
    
    return {"message": f"Пользователь {user.nickname} удалён"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
