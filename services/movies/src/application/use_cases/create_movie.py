"""Use Case: Создание нового фильма"""
from typing import List, Optional
from ...domain.entities.movie import Movie
from ...domain.value_objects.movie_title import MovieTitle
from ...domain.value_objects.year import Year
from ...domain.events.movie_events import MovieCreated
from ...domain.repositories.movie_repository import MovieRepository

class CreateMovieUseCase:
    """Сценарий: пользователь создаёт новый фильм"""
    
    def __init__(self, movie_repo: MovieRepository, event_bus=None):
        self.movie_repo = movie_repo
        self.event_bus = event_bus  # для отправки событий
    
    def execute(self, 
                title: str, 
                year: int, 
                director: str, 
                description: Optional[str] = None,
                actors: Optional[List[str]] = None) -> int:
        """
        Выполнить use case
        
        Args:
            title: название фильма
            year: год выпуска
            director: режиссёр
            description: описание
            actors: список актёров
            
        Returns:
            ID созданного фильма
            
        Raises:
            ValueError: если данные невалидны
        """
        # 1. Создаём Value Objects (валидация на входе)
        movie_title = MovieTitle(title)
        movie_year = Year(year)
        
        # 2. Создаём Entity
        movie = Movie(
            id=None,  # новый фильм
            title=movie_title,
            year=movie_year,
            director=director,
            description=description
        )
        
        # 3. Добавляем актёров (бизнес-логика)
        if actors:
            for actor in actors:
                movie.add_actor(actor)
        
        # 4. Сохраняем через репозиторий
        movie_id = self.movie_repo.save(movie)
        
        # 5. Отправляем событие
        if self.event_bus:
            self.event_bus.publish(MovieCreated(
                movie_id=movie_id,
                title=title,
                year=year,
                director=director
            ))
        
        return movie_id
