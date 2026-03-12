"""Сервис для работы с PostgreSQL"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from ..models.movie import Movie

class PostgresService:
    """Работа с PostgreSQL"""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Подключение к БД"""
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            cursor_factory=RealDictCursor
        )
    
    def get_all_movies(self, limit=100, offset=0):
        """Получить все фильмы"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, year, director, description, imdb_rating
                FROM movies
                ORDER BY id
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            return [Movie.from_db_row(
                (r['id'], r['title'], r['year'], r['director'], 
                 r['description'], r['imdb_rating'])
            ).to_dict() for r in rows]
    
    def get_movie_by_id(self, movie_id):
        """Получить фильм по ID"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, year, director, description, imdb_rating
                FROM movies
                WHERE id = %s
            """, (movie_id,))
            row = cur.fetchone()
            if row:
                return Movie.from_db_row(
                    (row['id'], row['title'], row['year'], row['director'],
                     row['description'], row['imdb_rating'])
                ).to_dict()
            return None
    
    def create_movie(self, movie_data):
        """Создать новый фильм"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO movies (title, year, director, description, imdb_rating)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                movie_data['title'],
                movie_data.get('year'),
                movie_data.get('director'),
                movie_data.get('description'),
                movie_data.get('imdb_rating')
            ))
            movie_id = cur.fetchone()['id']
            self.conn.commit()
            return movie_id
    
    def close(self):
        """Закрыть соединение"""
        if self.conn:
            self.conn.close()
