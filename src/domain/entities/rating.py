"""Entity: Оценка фильма пользователем"""
from datetime import datetime

class Rating:
    """Оценка фильма"""
    
    def __init__(self, 
                 user_id: int,
                 movie_id: int,
                 value: int,
                 created_at: datetime = None):
        self.user_id = user_id
        self.movie_id = movie_id
        self.value = value
        self.created_at = created_at or datetime.now()
        
        if self.value < 1 or self.value > 10:
            raise ValueError("Оценка должна быть от 1 до 10")
    
    def __eq__(self, other):
        if not isinstance(other, Rating):
            return False
        return (self.user_id == other.user_id and 
                self.movie_id == other.movie_id)
