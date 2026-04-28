import uuid
from typing import Optional

import uvicorn  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi import FastAPI, HTTPException, Response, Request, Depends  # type: ignore

from models import *
from dbs import *


app = FastAPI(title="Event Manager API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== Вспомогательные функции ==========
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


# ========== Эндпоинты ==========
@app.post("/login")
async def login(login_data: LoginRequest, response: Response):
    """Вход по паролю. Устанавливает сессионную куку."""
    user = get_user_by_password(login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    # Создаём сессию
    session_id = uuid.uuid4().hex
    sessions_db[session_id] = user.id
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # для localhost без HTTPS
        samesite="lax",
        path="/",  # обязательно укажите корневой путь
        max_age=60 * 60 * 24,  # время жизни 24 часа
    )
    return {
        "id": user.id,
        "nickname": user.nickname,
        "points": user.points,
        "company": user.company,
    }


@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions_db:
        del sessions_db[session_id]
    response.delete_cookie("session_id")
    return {"message": "Вы вышли"}


@app.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    """Возвращает профиль текущего авторизованного пользователя."""
    return {
        "nickname": user.nickname,
        "points": user.points,
        "company": user.company,
    }


@app.get("/events", response_model=List[EventResponse])
async def get_events(user: User = Depends(get_current_user)):
    """Возвращает активные события, помечая те, на которые пользователь уже зарегистрирован."""
    active_events = [e for e in events_db if not e.is_archived]
    result = []
    for event in active_events:
        registered = any(
            r.user_id == user.id and r.event_id == event.id for r in registrations_db
        )
        result.append(
            EventResponse(
                id=event.id,
                name=event.name,
                tags=event.tags,
                points=event.points,
                date=event.date,
                is_registered=registered,
            )
        )
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
