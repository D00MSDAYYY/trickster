# ========================== main.py ==========================
import uuid
import random
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_visible_fields import visible_fields_response

from dbs import *
from models.external import *

app = FastAPI(title="Event Manager API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Зависимости
# ---------------------------------------------------------------------------
def get_user_by_password(password: str) -> Optional[User]:
    for u in users_db:
        if u.password == password:
            return u
    return None


def get_current_user(request: Request) -> User:
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions_db:
        raise HTTPException(status_code=401, detail="Не авторизован")
    user_id = sessions_db[session_id]
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


def ensure_admin(user: User = Depends(get_current_user)):
    if user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user


def get_current_role(user: User = Depends(get_current_user)) -> Role:
    return user.role


# ---------------------------------------------------------------------------
# Аутентификация
# ---------------------------------------------------------------------------
@app.post("/login", response_model=UserInfoResponse)
async def login(login_data: LoginRequest, response: Response):
    user = get_user_by_password(login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    session_id = uuid.uuid4().hex
    sessions_db[session_id] = user.id  # type: ignore
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24,
    )
    return visible_fields_response(user, role=user.role)


@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions_db:
        del sessions_db[session_id]
    response.delete_cookie("session_id")
    return {"message": "Вы вышли"}


# ---------------------------------------------------------------------------
# Профиль
# ---------------------------------------------------------------------------
@app.get("/profile", response_model=UserInfoResponse)
async def get_profile(
    user: User = Depends(get_current_user), role: Role = Depends(get_current_role)
):
    return visible_fields_response(user, role=role)


@app.patch("/profile", response_model=UserInfoResponse)
async def update_profile(
    profile_data: UserInfoResponse,
    user: User = Depends(get_current_user),
    role: Role = Depends(get_current_role),
):
    data = profile_data.model_dump(
        exclude_unset=True,
        exclude={"id", "role", "created_at"},
    )
    for field, value in data.items():
        setattr(user, field, value)
    return visible_fields_response(user, role=role)


# ---------------------------------------------------------------------------
# События (пользовательская часть)
# ---------------------------------------------------------------------------


def event_to_response2(
    event: Event, role: Role, is_registered: Optional[bool] = None
) -> EventInfoResponse:

    data = visible_fields_response(event, role=role)
    
    # Собираем теги из связей
    tag_ids = [et.tag_id for et in event_tags_db if et.event_id == event.id]
    tags = [t for t in tags_db if t.id in tag_ids]
    tag_responses = [TagInfoResponse(**visible_fields_response(t, role=role).model_dump()) for t in tags]
    
    # Копируем данные и добавляем недостающие поля
    update_dict = data.model_dump()
    update_dict["tags"] = tag_responses
    if is_registered is not None:
        update_dict["is_registered"] = is_registered
    
    return EventInfoResponse(**update_dict)


@app.get("/events", response_model=List[EventInfoResponse])
async def get_events(
    user: User = Depends(get_current_user),
    role: Role = Depends(get_current_role),
):
    active = [e for e in events_db if not e.is_archived]
    result = []
    for e in active:
        is_reg = any(
            r.user_id == user.id and r.event_id == e.id for r in registrations_db
        )
        result.append(event_to_response2(e, role, is_reg))
    return result


@app.get("/events/{event_id}", response_model=EventInfoResponse)
async def get_event_detail(
    event_id: int,
    user: User = Depends(get_current_user),
    role: Role = Depends(get_current_role),
):
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    reg = any(r.user_id == user.id and r.event_id == event_id for r in registrations_db)
    return event_to_response2(event, role, reg)


@app.post("/events/{event_id}/register")
async def register_for_event(event_id: int, user: User = Depends(get_current_user)):
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    if event.is_archived:
        raise HTTPException(
            status_code=400, detail="Нельзя зарегистрироваться на прошедшее событие"
        )
    if any(r.user_id == user.id and r.event_id == event_id for r in registrations_db):
        raise HTTPException(status_code=409, detail="Вы уже зарегистрированы")
    registrations_db.append(Registration(user_id=user.id, event_id=event_id))  # type: ignore
    return {"message": f"Вы зарегистрированы на событие '{event.title}'"}


@app.delete("/events/{event_id}/register")
async def unregister_from_event(event_id: int, user: User = Depends(get_current_user)):
    reg = next(
        (
            r
            for r in registrations_db
            if r.user_id == user.id and r.event_id == event_id
        ),
        None,
    )
    if not reg:
        raise HTTPException(status_code=404, detail="Регистрация не найдена")
    registrations_db.remove(reg)
    event = next((e for e in events_db if e.id == event_id), None)
    return {"message": f"Регистрация на '{event.title}' отменена"}  # type: ignore


# ---------------------------------------------------------------------------
# Теги
# ---------------------------------------------------------------------------
@app.get("/tags", response_model=List[TagInfoResponse])
async def get_tags(role: Role = Depends(get_current_role)):
    return [visible_fields_response(t, role=role) for t in tags_db]


# ---------------------------------------------------------------------------
# Уведомления
# ---------------------------------------------------------------------------
@app.get("/notifications", response_model=List[NotificationInfoResponse])
async def get_notifications(role: Role = Depends(get_current_role)):
    return [visible_fields_response(n, role=role) for n in notifications_db]


# ---------------------------------------------------------------------------
# Административные эндпоинты
# ---------------------------------------------------------------------------
@app.get("/admin/events", response_model=List[EventInfoResponse])
async def get_admin_events(admin: User = Depends(ensure_admin)):
    return [event_to_response2(e, Role.admin) for e in events_db]


@app.post("/admin/events", response_model=EventInfoResponse)
async def create_event(
    event_data: EventInfoResponse, admin: User = Depends(ensure_admin)
):
    new_event = Event(**event_data.model_dump())  # type: ignore

    
    events_db.append(new_event)
    for (tag_id, tag_name) in event_data.tags:
        tag = next((t for t in tags_db if t.name.lower() == tag_name.lower()), None)
        if not tag:
            tag = Tag(id=max((t.id for t in tags_db), default=0) + 1, name=tag_name)
            tags_db.append(tag)
        event_tags_db.append(EventTagLink(event_id=new_event.id, tag_id=tag.id))

    return event_to_response2(new_event, Role.admin)


@app.patch("/admin/events/{event_id}", response_model=EventInfoResponse)
async def update_event(
    event_id: int, event_data: EventInfoResponse, admin: User = Depends(ensure_admin)
):
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    update_dict = event_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if field != "tags":
            setattr(event, field, value)
    if "tags" in update_dict:
        global event_tags_db
        event_tags_db = [et for et in event_tags_db if et.event_id != event_id]
        for tag_name in update_dict["tags"]:
            tag = next((t for t in tags_db if t.name.lower() == tag_name.lower()), None)
            if not tag:
                tag = Tag(id=max((t.id for t in tags_db), default=0) + 1, name=tag_name)
                tags_db.append(tag)
            event_tags_db.append(EventTagLink(event_id=event.id, tag_id=tag.id))
    return event_to_response2(event, Role.admin)


@app.delete("/admin/events/{event_id}")
async def delete_event(event_id: int, admin: User = Depends(ensure_admin)):
    global registrations_db, attendants_db, event_tags_db, events_db

    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    registrations_db = [r for r in registrations_db if r.event_id != event_id]
    attendants_db = [a for a in attendants_db if a.event_id != event_id]
    event_tags_db = [et for et in event_tags_db if et.event_id != event_id]
    events_db.remove(event)
    return {"message": f"Событие '{event.title}' удалено"}


# @app.get("/admin/users/search", response_model=List[UserSearchItem])
# async def search_users(q: str, admin: User = Depends(ensure_admin)):
#     if not q:
#         return []
#     q_lower = q.lower()
#     return [
#         UserSearchItem(id=u.id, nickname=u.nickname)
#         for u in users_db
#         if q_lower in u.nickname.lower()
#     ][:20]


# @app.get("/admin/events/{event_id}/attendants", response_model=List[UserSearchItem])
# async def get_event_attendants(event_id: int, admin: User = Depends(ensure_admin)):
#     event = next((e for e in events_db if e.id == event_id), None)
#     if not event:
#         raise HTTPException(status_code=404, detail="Событие не найдено")
#     attendant_ids = [a.user_id for a in attendants_db if a.event_id == event_id]
#     return [
#         UserSearchItem(id=u.id, nickname=u.nickname)
#         for u in users_db
#         if u.id in attendant_ids
#     ]


# @app.patch("/admin/events/{event_id}/attendants")
# async def update_event_attendants(
#     event_id: int, attendant_ids: List[int], admin: User = Depends(ensure_admin)
# ):
#     event = next((e for e in events_db if e.id == event_id), None)
#     if not event:
#         raise HTTPException(status_code=404, detail="Событие не найдено")
#     global attendants_db
#     attendants_db = [a for a in attendants_db if a.event_id != event_id]
#     for uid in attendant_ids:
#         attendants_db.append(Attendance(user_id=uid, event_id=event_id))
#     return {"message": "Список посетителей обновлён"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
