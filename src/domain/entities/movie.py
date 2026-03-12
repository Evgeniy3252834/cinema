"""Entity: Фильм"""
from typing import List, Optional
from ..value_objects.movie_title import MovieTitle
from ..value_objects.year import Year

class Movie:
    """Фильм - основная entity системы"""
    
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
        self._actors: List[str] = []
    
    def add_actor(self, actor: str) -> None:
        """Добавить актёра (бизнес-правило: не дублировать)"""
        if actor not in self._actors:
            self._actors.append(actor)
    
    @property
    def actors(self) -> List[str]:
        return self._actors.copy()
    
    def __eq__(self, other):
        if not isinstance(other, Movie):
            return False
        return self.id == other.id
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': str(self.title),
            'year': int(self.year),
            'director': self.director,
            'description': self.description,
            'actors': self.actors
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Movie':
        movie = cls(
            id=data.get('id'),
            title=MovieTitle(data['title']),
            year=Year(data['year']),
            director=data['director'],
            description=data.get('description')
        )
        for actor in data.get('actors', []):
            movie.add_actor(actor)
        return movie
