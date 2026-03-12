"""Доменные события для фильмов"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DomainEvent:
    """Базовый класс для всех событий"""
    occurred_at: datetime = datetime.now()

@dataclass
class MovieCreated(DomainEvent):
    """Событие: создан новый фильм"""
    movie_id: int
    title: str
    year: int
    director: str

@dataclass
class MovieRated(DomainEvent):
    """Событие: фильм оценён"""
    movie_id: int
    user_id: int
    rating: int
    old_rating: Optional[int] = None

@dataclass
class MovieViewed(DomainEvent):
    """Событие: фильм просмотрен"""
    movie_id: int
    user_id: int

@dataclass
class ActorAdded(DomainEvent):
    """Событие: добавлен актёр к фильму"""
    movie_id: int
    actor_name: str
