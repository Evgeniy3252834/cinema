"""Кэширование в Redis"""
import json
import redis
from typing import Optional, Any
from ...domain.entities.movie import Movie

class RedisCache:
    """Кэш на Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get_movie(self, movie_id: int) -> Optional[Movie]:
        """Получить фильм из кэша"""
        key = f"movie:{movie_id}"
        data = self.redis.get(key)
        if data:
            movie_data = json.loads(data)
            return Movie.from_dict(movie_data)
        return None
    
    def set_movie(self, movie_id: int, movie: Movie, ttl: int = 3600):
        """Сохранить фильм в кэш"""
        key = f"movie:{movie_id}"
        self.redis.setex(key, ttl, json.dumps(movie.to_dict()))
    
    def delete_movie(self, movie_id: int):
        """Удалить фильм из кэша"""
        key = f"movie:{movie_id}"
        self.redis.delete(key)
    
    def increment_views(self, movie_id: int) -> int:
        """Увеличить счётчик просмотров"""
        key = f"views:{movie_id}"
        return self.redis.incr(key)
    
    def get_top_movies(self, limit: int = 10) -> list:
        """Получить топ фильмов по просмотрам"""
        keys = self.redis.keys("views:*")
        result = []
        for key in keys:
            movie_id = int(key.split(':')[1])
            views = int(self.redis.get(key) or 0)
            result.append((movie_id, views))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:limit]
