"""Use Case: Создание нового фильма"""
from typing import List, Optional
from ...domain.entities.movie import Movie
from ...domain.value_objects.movie_title import MovieTitle
from ...domain.value_objects.year import Year
from ...domain.repositories.movie_repository import MovieRepository
from ...infrastructure.message_bus.movie_event_publisher import MovieEventPublisher

class CreateMovieUseCase:
    """Сценарий: пользователь создаёт новый фильм"""
    
    def __init__(self, 
                 movie_repo: MovieRepository, 
                 event_publisher: Optional[MovieEventPublisher] = None):
        self.movie_repo = movie_repo
        self.event_publisher = event_publisher
    
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
        
        # 5. Публикуем событие (асинхронно)
        if self.event_publisher:
            self.event_publisher.publish_movie_created(
                movie_id=movie_id,
                title=title,
                year=year,
                director=director,
                actors=actors or []
            )
        
        return movie_id
