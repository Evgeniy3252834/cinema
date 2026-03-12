"""Entity: Пользователь"""
from typing import List
from datetime import datetime
from .movie import Movie
from ..value_objects.rating import Rating

class User:
    """Пользователь системы"""
    
    def __init__(self, id: int, username: str, email: str):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = datetime.now()
        self._watch_history: List[Movie] = []
    
    def watch_movie(self, movie: Movie) -> None:
        """Добавить фильм в историю просмотров"""
        if movie not in self._watch_history:
            self._watch_history.append(movie)
    
    def get_recommendations(self) -> List[Movie]:
        """Получить рекомендации (бизнес-логика)"""
        # Здесь может быть сложная логика на основе истории
        # Пока заглушка
        return self._watch_history[-5:]  # последние 5
    
    @property
    def watch_history(self) -> List[Movie]:
        """История просмотров (копия)"""
        return self._watch_history.copy()
