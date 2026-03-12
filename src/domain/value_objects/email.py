"""Value Object: Email пользователя"""
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    """Email с валидацией"""
    value: str
    
    def __post_init__(self):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Некорректный email: {self.value}")
    
    def __str__(self):
        return self.value
