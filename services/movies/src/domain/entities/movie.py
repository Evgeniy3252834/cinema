"""Entity: Фильм"""
from typing import List, Optional
from ..value_objects.movie_title import MovieTitle
from ..value_objects.year import Year
from ..value_objects.rating import Rating

class Movie:
    """Фильм - главная entity в системе"""
    
    def __init__(self, 
                 id: Optional[int],
                 title: MovieTitle,
                 year: Year,
                 director: str,
                 description: Optional[str] = None):
        self.id = id
        self.title = title
        self.year = year
        self.director = director
        self.description = description
        self._ratings: List[Rating] = []
        self._actors: List[str] = []
    
    def add_rating(self, rating: Rating) -> None:
        """Добавить оценку фильму"""
        # Бизнес-правило: пользователь может оценить фильм только раз
        if any(r.user_id == rating.user_id for r in self._ratings):
            raise ValueError(f"User {rating.user_id} already rated this movie")
        
        self._ratings.append(rating)
    
    def add_actor(self, actor_name: str) -> None:
        """Добавить актёра"""
        if actor_name not in self._actors:
            self._actors.append(actor_name)
    
    @property
    def average_rating(self) -> float:
        """Средняя оценка фильма (бизнес-логика)"""
        if not self._ratings:
            return 0.0
        return sum(r.value for r in self._ratings) / len(self._ratings)
    
    @property
    def rating_count(self) -> int:
        """Количество оценок"""
        return len(self._ratings)
    
    @property
    def actors(self) -> List[str]:
        """Список актёров (копия для защиты)"""
        return self._actors.copy()
    
    def __eq__(self, other):
        """Две entity равны, если у них одинаковый ID"""
        if not isinstance(other, Movie):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """Для использования в множествах"""
        return hash(self.id)
