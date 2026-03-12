"""Интерфейс репозитория оценок"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ...entities.rating import Rating

class RatingRepository(ABC):
    """Абстрактный репозиторий для оценок"""
    
    @abstractmethod
    def save(self, rating: Rating) -> None:
        pass
    
    @abstractmethod
    def get_by_user_and_movie(self, user_id: int, movie_id: int) -> Optional[Rating]:
        pass
    
    @abstractmethod
    def get_by_movie(self, movie_id: int) -> List[Rating]:
        pass
    
    @abstractmethod
    def get_average_for_movie(self, movie_id: int) -> float:
        pass
