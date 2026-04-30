import uuid
import random
from typing import Optional

import uvicorn  # type: ignore
from fastapi import FastAPI, HTTPException, Response, Request, Depends  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from dbs import *

app = FastAPI(title="Event Manager API", version="0.2.0")

# --------------------------------------------------------------------------- #
#                                  CORS                                       #
# --------------------------------------------------------------------------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
#                         Зависимости и утилиты                               #
# --------------------------------------------------------------------------- #
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
    if user.role != Roles.admin:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user


# --------------------------------------------------------------------------- #
#                           Авторизация                                      #
# --------------------------------------------------------------------------- #
@app.post("/login")
async def login(login_data: LoginRequest, response: Response):
    """Вход по паролю, установка сессионной куки."""
    user = get_user_by_password(login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    session_id = uuid.uuid4().hex
    sessions_db[session_id] = user.id
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24,
    )
    return user


@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions_db:
        del sessions_db[session_id]
    response.delete_cookie("session_id")
    return {"message": "Вы вышли"}


# --------------------------------------------------------------------------- #
#                         Профиль пользователя                               #
# --------------------------------------------------------------------------- #
@app.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    """Возвращает профиль текущего пользователя."""
    return user


@app.patch("/profile")
async def update_profile(
    profile_data: ProfileUpdate, user: User = Depends(get_current_user)
):
    """Обновить настройки профиля."""
    if profile_data.company is not None:
        user.company = profile_data.company
    if profile_data.notify_three_days is not None:
        user.notify_three_days = profile_data.notify_three_days
    return user


# --------------------------------------------------------------------------- #
#                    События (общие для всех пользователей)                  #
# --------------------------------------------------------------------------- #
@app.get("/events", response_model=List[Event])
async def get_events(user: User = Depends(get_current_user)):
    """Активные события с отметкой is_registered и сортировкой."""
    active = [e for e in events_db if not e.is_archived]
    result = []
    for event in active:
        registered = any(
            r.user_id == user.id and r.event_id == event.id for r in registrations_db
        )
        result.append(
            Event(
                **event.model_dump(exclude={"is_registered"}),
                is_registered=registered,
            )
        )
    result.sort(key=lambda e: (not e.is_registered, e.date))
    return result


@app.get("/events/{event_id}", response_model=Event)
async def get_event_detail(event_id: int, user: User = Depends(get_current_user)):
    """Детальная информация о событии."""
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    registered = any(
        r.user_id == user.id and r.event_id == event_id for r in registrations_db
    )
    return Event(
        **event.model_dump(exclude={"is_registered"}),
        is_registered=registered,
    )


@app.post("/events/{event_id}/register")
async def register_for_event(event_id: int, user: User = Depends(get_current_user)):
    """Зарегистрироваться на событие."""
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    if event.is_archived:
        raise HTTPException(
            status_code=400, detail="Нельзя зарегистрироваться на прошедшее событие"
        )
    if any(r.user_id == user.id and r.event_id == event_id for r in registrations_db):
        raise HTTPException(status_code=409, detail="Вы уже зарегистрированы")

    registrations_db.append(Registration(user_id=user.id, event_id=event_id))
    return {"message": f"Вы зарегистрированы на событие '{event.name}'"}


@app.delete("/events/{event_id}/register")
async def unregister_from_event(event_id: int, user: User = Depends(get_current_user)):
    """Отменить регистрацию на событие."""
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

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
    return {"message": f"Регистрация на событие '{event.name}' отменена"}


# --------------------------------------------------------------------------- #
#                            Теги                                            #
# --------------------------------------------------------------------------- #
@app.get("/tags", response_model=List[Tag])
async def get_tags(user: User = Depends(get_current_user)):
    """Все доступные теги (для автодополнения)."""
    return tags_db


# --------------------------------------------------------------------------- #
#                         Уведомления                                        #
# --------------------------------------------------------------------------- #
@app.get("/notifications", response_model=List[Notification])
async def get_notifications(user: User = Depends(get_current_user)):
    """Уведомления текущего пользователя."""
    return [n for n in notifications_db]


# --------------------------------------------------------------------------- #
#                     Административные эндпоинты                             #
# --------------------------------------------------------------------------- #
@app.get("/admin/events", response_model=List[Event])
async def get_admin_events(admin: User = Depends(ensure_admin)):
    """Все события (админ-панель)."""
    return events_db


@app.post("/admin/events", response_model=Event)
async def create_event(event_data: Event, admin: User = Depends(ensure_admin)):
    """Создать новое событие (администратор)."""
    new_event = Event(
        **event_data.model_dump(exclude={"id"}),
        id=random.randint(0, 10_000_000),
    )
    events_db.append(new_event)
    return new_event


@app.patch("/admin/events/{event_id}", response_model=Event)
async def update_event(
    event_id: int, event_data: Event, admin: User = Depends(ensure_admin)
):
    """Обновить существующее событие (администратор)."""
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    update_data = event_data.model_dump(
        exclude_unset=True,
        exclude={"id"},
    )
    for field, value in update_data.items():
        setattr(event, field, value)
    return event

@app.delete("/admin/events/{event_id}")
async def delete_event(event_id: int, admin: User = Depends(ensure_admin)):
    """Удалить событие (администратор)."""
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    # Удаляем все связанные регистрации
    global registrations_db
    registrations_db = [r for r in registrations_db if r.event_id != event_id]

    # Удаляем всех посетителей (если есть attendants)
    global attendants_db
    attendants_db = [a for a in attendants_db if a.event_id != event_id]

    # Удаляем само событие
    events_db.remove(event)
    return {"message": f"Событие '{event.name}' удалено"}


@app.get("/admin/users/search", response_model=List[UserSearchItem])
async def search_users(q: str, admin: User = Depends(ensure_admin)):
    """Поиск пользователей по нику (админ)."""
    if not q:
        return []
    q_lower = q.lower()
    return [
        UserSearchItem(id=u.id, nickname=u.nickname)
        for u in users_db
        if q_lower in u.nickname.lower()
    ][
        :20
    ]  # ограничим до 20 результатов


@app.get("/admin/events/{event_id}/attendants", response_model=List[UserSearchItem])
async def get_event_attendants(event_id: int, admin: User = Depends(ensure_admin)):
    """Получить список посетителей мероприятия (админ)."""
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    attendant_ids = [a.user_id for a in attendants_db if a.event_id == event_id]
    return [
        UserSearchItem(id=u.id, nickname=u.nickname)
        for u in users_db
        if u.id in attendant_ids
    ]


@app.patch("/admin/events/{event_id}/attendants")
async def update_event_attendants(
    event_id: int, attendant_ids: List[int], admin: User = Depends(ensure_admin)
):
    event = next((e for e in events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    global attendants_db
    attendants_db = [a for a in attendants_db if a.event_id != event_id]
    for uid in attendant_ids:
        attendants_db.append(Attendance(user_id=uid, event_id=event_id))

    return {"message": "Список посетителей обновлён"}


# --------------------------------------------------------------------------- #
#                              Запуск                                        #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
