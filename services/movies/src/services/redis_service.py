"""Сервис для кэширования в Redis"""
import redis
import json
import os
from typing import Any, Optional

class RedisService:
    """Кэширование данных в Redis"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
    
    def cache_movie(self, movie_id: int, movie_data: dict, ttl: int = 3600) -> None:
        """
        Сохранить фильм в кэш
        
        Args:
            movie_id: ID фильма
            movie_data: данные фильма
            ttl: время жизни в секундах (по умолчанию 1 час)
        """
        key = f"movie:{movie_id}"
        self.client.setex(key, ttl, json.dumps(movie_data))
    
    def get_cached_movie(self, movie_id: int) -> Optional[dict]:
        """
        Получить фильм из кэша
        
        Args:
            movie_id: ID фильма
            
        Returns:
            dict или None, если фильма нет в кэше
        """
        key = f"movie:{movie_id}"
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def cache_movies_list(self, key: str, movies_data: list, ttl: int = 300) -> None:
        """
        Сохранить список фильмов в кэш
        
        Args:
            key: ключ кэша
            movies_data: список фильмов
            ttl: время жизни в секундах (по умолчанию 5 минут)
        """
        self.client.setex(key, ttl, json.dumps(movies_data))
    
    def get_cached_movies_list(self, key: str) -> Optional[list]:
        """
        Получить список фильмов из кэша
        
        Args:
            key: ключ кэша
            
        Returns:
            list или None, если данных нет в кэше
        """
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def invalidate_movie_cache(self, movie_id: int) -> None:
        """Инвалидировать кэш фильма"""
        self.client.delete(f"movie:{movie_id}")
        # Также инвалидируем списки
        self.client.delete("movies:all")
        self.client.delete("movies:top")
    
    def increment_views(self, movie_id: int) -> int:
        """
        Увеличить счётчик просмотров фильма
        
        Args:
            movie_id: ID фильма
            
        Returns:
            новое значение счётчика
        """
        key = f"views:movie:{movie_id}"
        return self.client.incr(key)
    
    def get_top_movies(self, limit: int = 10) -> list:
        """
        Получить топ фильмов по просмотрам
        
        Args:
            limit: количество фильмов
            
        Returns:
            список (movie_id, views)
        """
        # Получаем все ключи просмотров
        keys = self.client.keys("views:movie:*")
        result = []
        
        for key in keys:
            movie_id = int(key.split(':')[-1])
            views = int(self.client.get(key) or 0)
            result.append((movie_id, views))
        
        # Сортируем по убыванию и возвращаем топ
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:limit]
    
    def ping(self) -> bool:
        """Проверить подключение к Redis"""
        try:
            return self.client.ping()
        except:
            return False
