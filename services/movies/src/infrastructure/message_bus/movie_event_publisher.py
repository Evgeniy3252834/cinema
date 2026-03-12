"""Публикация событий фильмов"""
import uuid
from typing import List
from ...domain.events.integration_events import (
    MovieCreatedIntegrationEvent,
    MovieRatedIntegrationEvent,
    MovieViewedIntegrationEvent
)
from .event_bus import EventBus

class MovieEventPublisher:
    """Публикует события, связанные с фильмами"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.EXCHANGE_NAME = 'cinematch.movies'
        
        # Инициализируем exchange
        self.event_bus.declare_exchange(self.EXCHANGE_NAME, 'topic')
    
    def publish_movie_created(self, movie_id: int, title: str, 
                              year: int, director: str, actors: List[str]):
        """Опубликовать событие создания фильма"""
        event = MovieCreatedIntegrationEvent(
            event_id=str(uuid.uuid4()),
            movie_id=movie_id,
            title=title,
            year=year,
            director=director,
            actors=actors
        )
        
        self.event_bus.publish(
            exchange_name=self.EXCHANGE_NAME,
            routing_key='movie.created',
            event=event
        )
    
    def publish_movie_rated(self, movie_id: int, user_id: int, 
                            rating: int, old_rating: int = None):
        """Опубликовать событие оценки фильма"""
        event = MovieRatedIntegrationEvent(
            event_id=str(uuid.uuid4()),
            movie_id=movie_id,
            user_id=user_id,
            rating=rating,
            old_rating=old_rating
        )
        
        self.event_bus.publish(
            exchange_name=self.EXCHANGE_NAME,
            routing_key='movie.rated',
            event=event
        )
    
    def publish_movie_viewed(self, movie_id: int, user_id: int):
        """Опубликовать событие просмотра фильма"""
        event = MovieViewedIntegrationEvent(
            event_id=str(uuid.uuid4()),
            movie_id=movie_id,
            user_id=user_id,
            timestamp=event.occurred_at
        )
        
        self.event_bus.publish(
            exchange_name=self.EXCHANGE_NAME,
            routing_key='movie.viewed',
            event=event
        )
