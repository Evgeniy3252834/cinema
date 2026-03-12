"""Интерфейс репозитория для фильмов"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.movie import Movie

class MovieRepository(ABC):
    """Абстрактный репозиторий для фильмов"""
    
    @abstractmethod
    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        """Получить фильм по ID"""
        pass
    
    @abstractmethod
    def get_by_title(self, title: str) -> Optional[Movie]:
        """Получить фильм по названию"""
        pass
    
    @abstractmethod
    def save(self, movie: Movie) -> int:
        """Сохранить фильм (создать или обновить)"""
        pass
    
    @abstractmethod
    def delete(self, movie_id: int) -> bool:
        """Удалить фильм"""
        pass
    
    @abstractmethod
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Movie]:
        """Получить все фильмы"""
        pass
    
    @abstractmethod
    def get_by_director(self, director: str) -> List[Movie]:
        """Получить фильмы режиссёра"""
        pass
