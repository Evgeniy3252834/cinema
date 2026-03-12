"""Consumer для событий фильмов"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from infrastructure.message_bus.event_bus import EventBus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieEventsConsumer:
    """Слушает события фильмов и обновляет рекомендации"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.EXCHANGE_NAME = 'cinematch.movies'
        self.QUEUE_NAME = 'recommendations.movie_events'
        
        # Инициализируем
        self._setup()
    
    def _setup(self):
        """Настройка очереди и привязок"""
        # Создаём очередь
        self.event_bus.declare_queue(self.QUEUE_NAME)
        
        # Привязываем к нужным routing_key
        self.event_bus.bind_queue(
            self.QUEUE_NAME,
            self.EXCHANGE_NAME,
            'movie.created'
        )
        self.event_bus.bind_queue(
            self.QUEUE_NAME,
            self.EXCHANGE_NAME,
            'movie.rated'
        )
        
        logger.info(f"✅ Consumer setup complete for queue: {self.QUEUE_NAME}")
    
    def handle_movie_created(self, event_data):
        """Обработка события создания фильма"""
        logger.info(f"🎬 New movie created: {event_data.get('title')}")
        # TODO: генерировать эмбеддинг для нового фильма
        # и сохранять в Qdrant
        print(f"Would generate embedding for movie: {event_data}")
    
    def handle_movie_rated(self, event_data):
        """Обработка события оценки фильма"""
        logger.info(f"⭐ Movie rated: {event_data.get('movie_id')} by user {event_data.get('user_id')}")
        # TODO: обновить персональные рекомендации
        print(f"Would update recommendations for user: {event_data}")
    
    def callback(self, event_data):
        """Общий callback, диспатчит по типу события"""
        event_type = event_data.get('_event_type')
        
        if event_type == 'MovieCreatedIntegrationEvent':
            self.handle_movie_created(event_data)
        elif event_type == 'MovieRatedIntegrationEvent':
            self.handle_movie_rated(event_data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def start(self):
        """Запустить потребление"""
        logger.info("🚀 Starting movie events consumer...")
        self.event_bus.consume(self.QUEUE_NAME, self.callback)
        self.event_bus.start_consuming()
