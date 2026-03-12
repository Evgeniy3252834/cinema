"""Интеграционные события для межсервисного взаимодействия"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class IntegrationEvent:
    """Базовый класс для интеграционных событий"""
    event_id: str
    occurred_at: datetime = datetime.now()

@dataclass
class MovieCreatedIntegrationEvent(IntegrationEvent):
    """Событие: фильм создан (для других сервисов)"""
    movie_id: int
    title: str
    year: int
    director: str
    actors: List[str]

@dataclass
class MovieRatedIntegrationEvent(IntegrationEvent):
    """Событие: фильм оценён"""
    movie_id: int
    user_id: int
    rating: int
    old_rating: Optional[int] = None

@dataclass
class MovieViewedIntegrationEvent(IntegrationEvent):
    """Событие: фильм просмотрен"""
    movie_id: int
    user_id: int
    timestamp: datetime

@dataclass
class RecommendationRequestedEvent(IntegrationEvent):
    """Событие: запрошены рекомендации"""
    user_id: int
    movie_id: int
    count: int = 10
