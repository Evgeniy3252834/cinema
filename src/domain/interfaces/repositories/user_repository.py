"""Интерфейс репозитория пользователей"""
from abc import ABC, abstractmethod
from typing import Optional
from ...entities.user import User
from ...value_objects.email import Email

class UserRepository(ABC):
    """Абстрактный репозиторий для пользователей"""
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> int:
        pass
