"""Value Object: Год выпуска фильма"""
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Year:
    """Год выпуска - с валидацией"""
    value: int
    
    def __post_init__(self):
        current_year = datetime.now().year
        if self.value < 1888:
            raise ValueError(f"Год {self.value} слишком ранний")
        if self.value > current_year + 5:
            raise ValueError(f"Год {self.value} слишком далёкое будущее")
    
    def __int__(self):
        return self.value
