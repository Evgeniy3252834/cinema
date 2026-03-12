"""Use Case: Создание нового фильма"""
from typing import List, Optional
from ...domain.entities.movie import Movie
from ...domain.value_objects.movie_title import MovieTitle
from ...domain.value_objects.year import Year
from ...domain.interfaces.repositories.movie_repository import MovieRepository
from ...infrastructure.database.neo4j.repositories.neo4j_graph_repository import Neo4jGraphRepository

class CreateMovieUseCase:
    """Сценарий создания фильма"""
    
    def __init__(self, 
                 movie_repo: MovieRepository,
                 graph_repo: Optional[Neo4jGraphRepository] = None):
        self.movie_repo = movie_repo
        self.graph_repo = graph_repo
    
    def execute(self, 
                title: str,
                year: int,
                director: str,
                description: Optional[str] = None,
                actors: Optional[List[str]] = None) -> int:
        """Создать новый фильм"""
        
        # 1. Создаём Value Objects (валидация)
        movie_title = MovieTitle(title)
        movie_year = Year(year)
        
        # 2. Создаём Entity
        movie = Movie(
            id=None,
            title=movie_title,
            year=movie_year,
            director=director,
            description=description
        )
        
        # 3. Добавляем актёров
        if actors:
            for actor in actors:
                movie.add_actor(actor)
        
        # 4. Сохраняем в PostgreSQL
        movie_id = self.movie_repo.save(movie)
        
        # 5. Сохраняем в Neo4j (граф)
        if self.graph_repo:
            self.graph_repo.add_movie(title, year, director)
            if actors:
                for actor in actors:
                    self.graph_repo.add_actor(title, actor)
        
        return movie_id
