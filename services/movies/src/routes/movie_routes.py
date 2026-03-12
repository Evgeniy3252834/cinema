"""Маршруты для работы с фильмами"""
from flask import Blueprint, request, jsonify, current_app
from ..services.postgres_service import PostgresService
from ..services.neo4j_service import Neo4jService
from ..services.redis_service import RedisService
import logging

# Создаём Blueprint
movies_bp = Blueprint('movies', __name__)

# Инициализируем сервисы (в реальном приложении лучше через Dependency Injection)
pg_service = PostgresService()
neo4j_service = Neo4jService()
redis_service = RedisService()

logger = logging.getLogger(__name__)

@movies_bp.route('/', methods=['GET'])
def get_movies():
    """
    Получить список всех фильмов
    ---
    tags:
      - movies
    responses:
      200:
        description: Список фильмов
    """
    try:
        # Пробуем из кэша
        cached = redis_service.get_cached_movies_list('movies:all')
        if cached:
            logger.info("Movies retrieved from cache")
            return jsonify({
                'source': 'redis',
                'data': cached
            })
        
        # Из PostgreSQL
        movies = pg_service.get_all_movies()
        
        # Сохраняем в кэш
        redis_service.cache_movies_list('movies:all', movies)
        logger.info(f"Movies retrieved from PostgreSQL, count: {len(movies)}")
        
        return jsonify({
            'source': 'postgresql',
            'data': movies
        })
    except Exception as e:
        logger.error(f"Error getting movies: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """
    Получить фильм по ID
    ---
    tags:
      - movies
    parameters:
      - name: movie_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Данные фильма
      404:
        description: Фильм не найден
    """
    try:
        # Пробуем из кэша
        cached = redis_service.get_cached_movie(movie_id)
        if cached:
            logger.info(f"Movie {movie_id} retrieved from cache")
            return jsonify({
                'source': 'redis',
                'data': cached
            })
        
        # Из PostgreSQL
        movie = pg_service.get_movie_by_id(movie_id)
        if not movie:
            logger.warning(f"Movie {movie_id} not found")
            return jsonify({'error': 'Movie not found'}), 404
        
        # Сохраняем в кэш
        redis_service.cache_movie(movie_id, movie)
        
        # Увеличиваем счётчик просмотров
        redis_service.increment_views(movie_id)
        
        logger.info(f"Movie {movie_id} retrieved from PostgreSQL")
        return jsonify({
            'source': 'postgresql',
            'data': movie
        })
    except Exception as e:
        logger.error(f"Error getting movie {movie_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@movies_bp.route('/', methods=['POST'])
def create_movie():
    """
    Создать новый фильм
    ---
    tags:
      - movies
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            title:
              type: string
            year:
              type: integer
            director:
              type: string
            description:
              type: string
            imdb_rating:
              type: number
            actors:
              type: array
              items:
                type: string
    responses:
      201:
        description: Фильм создан
      400:
        description: Ошибка валидации
    """
    try:
        data = request.json
        
        # Валидация
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        # Сохраняем в PostgreSQL
        movie_id = pg_service.create_movie(data)
        
        # Инвалидируем кэш
        redis_service.invalidate_movie_cache(movie_id)
        
        # Если есть актёры, сохраняем в Neo4j
        if 'actors' in data and data['actors']:
            neo4j_service.add_movie_with_actors(
                data['title'],
                data.get('year'),
                data.get('director', 'Unknown'),
                data['actors']
            )
            logger.info(f"Added {len(data['actors'])} actors to Neo4j for movie {movie_id}")
        
        logger.info(f"Movie created with ID: {movie_id}")
        return jsonify({
            'message': 'Movie created successfully',
            'id': movie_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating movie: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@movies_bp.route('/<int:movie_id>/actors', methods=['GET'])
def get_movie_actors(movie_id):
    """
    Получить актёров фильма (из Neo4j)
    ---
    tags:
      - movies
    parameters:
      - name: movie_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Список актёров
      404:
        description: Фильм не найден
    """
    try:
        # Сначала получим название фильма
        movie = pg_service.get_movie_by_id(movie_id)
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
        
        # Получаем актёров из Neo4j
        actors = neo4j_service.get_actors_by_movie(movie['title'])
        
        logger.info(f"Retrieved {len(actors)} actors for movie {movie_id}")
        return jsonify({
            'movie_id': movie_id,
            'movie_title': movie['title'],
            'actors': actors,
            'source': 'neo4j'
        })
    except Exception as e:
        logger.error(f"Error getting actors for movie {movie_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@movies_bp.route('/actors/<actor_name>/movies', methods=['GET'])
def get_actor_movies(actor_name):
    """
    Получить все фильмы актёра (из Neo4j)
    ---
    tags:
      - movies
    parameters:
      - name: actor_name
        in: path
        type: string
        required: true
    responses:
      200:
        description: Список фильмов
    """
    try:
        movies = neo4j_service.get_movies_by_actor(actor_name)
        logger.info(f"Retrieved {len(movies)} movies for actor {actor_name}")
        return jsonify({
            'actor': actor_name,
            'movies': movies,
            'source': 'neo4j'
        })
    except Exception as e:
        logger.error(f"Error getting movies for actor {actor_name}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@movies_bp.route('/top-views', methods=['GET'])
def top_by_views():
    """
    Топ фильмов по просмотрам (из Redis)
    ---
    tags:
      - movies
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 10
    responses:
      200:
        description: Топ фильмов
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        top_movies = redis_service.get_top_movies(limit)
        
        # Обогащаем данными из PostgreSQL
        result = []
        for movie_id, views in top_movies:
            movie = pg_service.get_movie_by_id(movie_id)
            if movie:
                result.append({
                    'id': movie_id,
                    'title': movie['title'],
                    'views': views
                })
        
        return jsonify({
            'source': 'redis',
            'data': result
        })
    except Exception as e:
        logger.error(f"Error getting top movies: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
