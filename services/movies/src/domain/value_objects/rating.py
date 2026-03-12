"""Value Object: Оценка фильма"""
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Rating:
    """Оценка фильма пользователем"""
    value: int
    user_id: int
    created_at: datetime
    
    def __post_init__(self):
        if self.value < 1 or self.value > 10:
            raise ValueError("Rating must be between 1 and 10")
        if self.user_id <= 0:
            raise ValueError("Invalid user ID")
    
    def __int__(self):
        return self.value
