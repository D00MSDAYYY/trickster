# ========================== dbs.py ==========================
from datetime import datetime, timedelta
from typing import List, Optional
from models.internal import *
from models.external import *

# ---------------------------------------------------------------------------
# Хранилища (эмуляция таблиц)
# ---------------------------------------------------------------------------
users_db: List[User] = []
tags_db: List[Tag] = []
events_db: List[Event] = []
event_tags_db: List[EventTagLink] = []
registrations_db: List[Registration] = []
attendants_db: List[Attendance] = []
notifications_db: List[Notification] = []
sessions_db: dict[str, int] = {}

# ========== Пользователи ==========
users_db = [
    User(id=1, nickname="admin", firstname="Админ", lastname="Админов",
         points=999, company="Администрация", password="1", role=Role.admin),
    User(id=2, nickname="ivanov", firstname="Иван", lastname="Иванов",
         points=150, company="Росагро", password="12", role=Role.user),
    User(id=3, nickname="petrov", firstname="Пётр", lastname="Петров",
         points=200, company="Роскосмос", password="123", role=Role.user),
    User(id=4, nickname="sidorov", firstname="Сидор", lastname="Сидоров",
         points=22, password="1234", role=Role.user),
    User(id=5, nickname="zaycev", firstname="Заяц", lastname="Зайцев",
         points=22, password="12345", role=Role.user),
    User(id=6, nickname="demidov", firstname="Демид", lastname="Демидов",
         points=22, company="Росатом", password="123456", role=Role.user),
    User(id=7, nickname="nuriev", firstname="Нури", lastname="Нуриев",
         points=22, company="АМС", password="1234567", role=Role.user),
]

# ========== Теги ==========
tags_db = [
    Tag(id=1, name="React"), Tag(id=2, name="Frontend"), Tag(id=3, name="Python"),
    Tag(id=4, name="Backend"), Tag(id=5, name="API"), Tag(id=6, name="VK"),
    Tag(id=7, name="Mini Apps"), Tag(id=8, name="Сообщество"), Tag(id=9, name="iOS"),
    Tag(id=10, name="Android"), Tag(id=11, name="Flutter"), Tag(id=12, name="Data Science"),
    Tag(id=13, name="Аналитика"), Tag(id=14, name="DevOps"), Tag(id=15, name="Docker"),
    Tag(id=16, name="Kubernetes"), Tag(id=17, name="Хакатон"), Tag(id=18, name="Медицина"),
    Tag(id=19, name="Алгоритмы"), Tag(id=20, name="C++"),
]

# ========== События ==========
events_db = [
    Event(id=1, title="Конференция VK Mini Apps",
          description="Ежегодная конференция для разработчиков мини-приложений ВКонтакте.",
          points=150, date=datetime(2025, 6, 15, 10, 0),
          link="https://vk.com/dev/events", is_archived=False),
    Event(id=2, title="React Advanced: Мастер-класс",
          description="Углубленный мастер-класс по продвинутым техникам React.",
          points=200, date=datetime(2025, 6, 20, 14, 0), is_archived=False),
    Event(id=3, title="Python для анализа данных",
          description="Введение в Python с акцентом на анализ данных.",
          points=100, date=datetime(2025, 7, 1, 18, 0), is_archived=False),
    Event(id=4, title="Хакатон «Код здоровья»",
          description="Соревнование по созданию IT-решений для медицины.",
          points=300, date=datetime(2025, 7, 10, 9, 0),
          link="https://healthcode.example.com", is_archived=False),
    Event(id=5, title="Старый Новый Год (архив)",
          description="Давно прошедшее праздничное мероприятие.",
          points=50, date=datetime(2023, 1, 14, 20, 0), is_archived=True),
    Event(id=6, title="Основы Docker (архив)",
          description="Практический воркшоп по контейнеризации.",
          points=120, date=datetime(2024, 9, 1, 10, 0), is_archived=True),
]

# ========== Связи событие-тег ==========
event_tags_db = [
    EventTagLink(event_id=1, tag_id=6),  # VK
    EventTagLink(event_id=1, tag_id=7),  # Mini Apps
    EventTagLink(event_id=2, tag_id=1),  # React
    EventTagLink(event_id=2, tag_id=2),  # Frontend
    EventTagLink(event_id=3, tag_id=3),  # Python
    EventTagLink(event_id=3, tag_id=12), # Data Science
    EventTagLink(event_id=3, tag_id=13), # Аналитика
    EventTagLink(event_id=4, tag_id=17), # Хакатон
    EventTagLink(event_id=4, tag_id=18), # Медицина
    EventTagLink(event_id=4, tag_id=3),  # Python
    EventTagLink(event_id=5, tag_id=17), # Хакатон
    EventTagLink(event_id=6, tag_id=15), # Docker
    EventTagLink(event_id=6, tag_id=14), # DevOps
]

# ========== Уведомления ==========
notifications_db = [
    Notification(id=1, title="Конференция уже завтра!",
                 body="Не забудьте посетить конференцию VK Mini Apps завтра в 10:00."),
    Notification(id=2, title="Новое событие добавлено",
                 body="Открыта регистрация на хакатон «Код здоровья»."),
    Notification(id=3, title="Изменение в расписании",
                 body="React мастер-класс перенесён на 20 июня 14:00."),
]

# ========== Регистрации ==========
registrations_db = [
    Registration(user_id=2, event_id=1),
    Registration(user_id=2, event_id=2),
    Registration(user_id=3, event_id=3),
    Registration(user_id=3, event_id=4),
    Registration(user_id=1, event_id=1),
]

# ========== Посетители ==========
attendants_db = [
    Attendance(user_id=2, event_id=1),
    Attendance(user_id=3, event_id=1),
]

event_id_counter = max(e.id for e in events_db) + 1