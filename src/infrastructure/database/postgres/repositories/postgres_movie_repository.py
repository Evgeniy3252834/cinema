"""Реализация репозитория фильмов для PostgreSQL"""
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from .....domain.entities.movie import Movie
from .....domain.value_objects.movie_title import MovieTitle
from .....domain.value_objects.year import Year
from .....domain.interfaces.repositories.movie_repository import MovieRepository

class PostgresMovieRepository(MovieRepository):
    """PostgreSQL реализация репозитория фильмов"""
    
    def __init__(self, connection):
        self.conn = connection
    
    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Получаем фильм
            cur.execute("""
                SELECT id, title, year, director, description 
                FROM movies WHERE id = %s
            """, (movie_id,))
            row = cur.fetchone()
            
            if not row:
                return None
            
            # Создаём объект фильма
            movie = Movie(
                id=row['id'],
                title=MovieTitle(row['title']),
                year=Year(row['year']),
                director=row['director'],
                description=row['description']
            )
            
            # Загружаем актёров
            cur.execute("""
                SELECT actor_name FROM movie_actors WHERE movie_id = %s
            """, (movie_id,))
            for actor_row in cur.fetchall():
                movie.add_actor(actor_row['actor_name'])
            
            return movie
    
    def save(self, movie: Movie) -> int:
        with self.conn.cursor() as cur:
            if movie.id is None:
                # CREATE
                cur.execute("""
                    INSERT INTO movies (title, year, director, description)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (str(movie.title), int(movie.year), 
                      movie.director, movie.description))
                movie_id = cur.fetchone()[0]
                
                # Сохраняем актёров
                for actor in movie.actors:
                    cur.execute("""
                        INSERT INTO movie_actors (movie_id, actor_name)
                        VALUES (%s, %s)
                    """, (movie_id, actor))
                
                self.conn.commit()
                return movie_id
            else:
                # UPDATE
                cur.execute("""
                    UPDATE movies 
                    SET title=%s, year=%s, director=%s, description=%s
                    WHERE id=%s
                """, (str(movie.title), int(movie.year), 
                      movie.director, movie.description, movie.id))
                
                # Обновляем актёров (удаляем старых, добавляем новых)
                cur.execute("DELETE FROM movie_actors WHERE movie_id = %s", (movie.id,))
                for actor in movie.actors:
                    cur.execute("""
                        INSERT INTO movie_actors (movie_id, actor_name)
                        VALUES (%s, %s)
                    """, (movie.id, actor))
                
                self.conn.commit()
                return movie.id
    
    def delete(self, movie_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM movie_actors WHERE movie_id = %s", (movie_id,))
            cur.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
            deleted = cur.rowcount > 0
            self.conn.commit()
            return deleted
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Movie]:
        movies = []
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, title, year, director, description 
                FROM movies ORDER BY id LIMIT %s OFFSET %s
            """, (limit, offset))
            
            for row in cur.fetchall():
                movie = Movie(
                    id=row['id'],
                    title=MovieTitle(row['title']),
                    year=Year(row['year']),
                    director=row['director'],
                    description=row['description']
                )
                
                # Загружаем актёров для каждого фильма
                cur.execute("""
                    SELECT actor_name FROM movie_actors WHERE movie_id = %s
                """, (row['id'],))
                for actor_row in cur.fetchall():
                    movie.add_actor(actor_row['actor_name'])
                
                movies.append(movie)
        
        return movies
    
    def get_by_title(self, title: str) -> Optional[Movie]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id FROM movies WHERE title = %s
            """, (title,))
            row = cur.fetchone()
            if row:
                return self.get_by_id(row['id'])
            return None
