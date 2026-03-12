"""Value Object: Год выпуска фильма"""
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Year:
    """Год выпуска - с валидацией"""
    value: int
    
    def __post_init__(self):
        current_year = datetime.now().year
        if self.value < 1888:  # Год первого фильма
            raise ValueError(f"Year {self.value} is too early (first movie was 1888)")
        if self.value > current_year + 5:  # Плюс 5 лет на будущие релизы
            raise ValueError(f"Year {self.value} is in far future")
    
    def __int__(self):
        return self.value
