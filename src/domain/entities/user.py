"""Entity: Пользователь"""
from typing import List
from ..value_objects.email import Email

class User:
    """Пользователь системы"""
    
    def __init__(self, id: int, username: str, email: Email):
        self.id = id
        self.username = username
        self.email = email
        self._watch_history: List[int] = []  # список movie_id
    
    def add_to_history(self, movie_id: int) -> None:
        """Добавить фильм в историю просмотров"""
        if movie_id not in self._watch_history:
            self._watch_history.append(movie_id)
    
    @property
    def watch_history(self) -> List[int]:
        return self._watch_history.copy()
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.id == other.id
