"""Value Object: Название фильма"""
from dataclasses import dataclass

@dataclass(frozen=True)
class MovieTitle:
    """Название фильма - неизменяемый объект с валидацией"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Название фильма не может быть пустым")
        if len(self.value) > 255:
            raise ValueError("Название фильма слишком длинное (максимум 255 символов)")
    
    def __str__(self):
        return self.value
