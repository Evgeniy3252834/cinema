"""Value Object: Название фильма"""
from dataclasses import dataclass

@dataclass(frozen=True)
class MovieTitle:
    """Название фильма - неизменяемый объект"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Movie title cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Movie title too long (max 255 chars)")
    
    def __str__(self):
        return self.value
