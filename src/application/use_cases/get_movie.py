"""Use Case: Получение фильма по ID"""
from typing import Optional
from ...domain.entities.movie import Movie
from ...domain.interfaces.repositories.movie_repository import MovieRepository
from ...infrastructure.cache.redis_cache import RedisCache

class GetMovieUseCase:
    """Сценарий получения деталей фильма"""
    
    def __init__(self, 
                 movie_repo: MovieRepository,
                 cache: Optional[RedisCache] = None):
        self.movie_repo = movie_repo
        self.cache = cache
    
    def execute(self, movie_id: int) -> Optional[Movie]:
        """Выполнить use case"""
        # 1. Проверяем кэш
        if self.cache:
            cached = self.cache.get_movie(movie_id)
            if cached:
                return cached
        
        # 2. Идём в БД
        movie = self.movie_repo.get_by_id(movie_id)
        
        # 3. Сохраняем в кэш
        if movie and self.cache:
            self.cache.set_movie(movie_id, movie)
            self.cache.increment_views(movie_id)
        
        return movie
