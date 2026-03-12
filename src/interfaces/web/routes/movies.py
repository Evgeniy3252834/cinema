"""Роуты для работы с фильмами"""
from flask import Blueprint, request, jsonify
import psycopg2
import redis
from neo4j import GraphDatabase
import os

from ....application.use_cases.get_movie import GetMovieUseCase
from ....application.use_cases.create_movie import CreateMovieUseCase
from ....application.use_cases.recommend_movies import RecommendMoviesUseCase
from ....infrastructure.database.postgres.repositories.postgres_movie_repository import PostgresMovieRepository
from ....infrastructure.database.neo4j.repositories.neo4j_graph_repository import Neo4jGraphRepository
from ....infrastructure.cache.redis_cache import RedisCache

movies_bp = Blueprint('movies', __name__)

# Подключения к БД
def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', 5432),
        dbname=os.getenv('POSTGRES_DB', 'cinematch'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )

def get_redis_client():
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True
    )

def get_neo4j_driver():
    return GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USER', 'neo4j'), 
              os.getenv('NEO4J_PASSWORD', 'password'))
    )

@movies_bp.route('/', methods=['GET'])
def get_movies():
    """Получить все фильмы"""
    conn = get_postgres_conn()
    repo = PostgresMovieRepository(conn)
    
    try:
        movies = repo.get_all()
        return jsonify({
            'movies': [m.to_dict() for m in movies]
        })
    finally:
        conn.close()

@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Получить фильм по ID"""
    conn = get_postgres_conn()
    redis_client = get_redis_client()
    
    try:
        repo = PostgresMovieRepository(conn)
        cache = RedisCache(redis_client)
        
        use_case = GetMovieUseCase(repo, cache)
        movie = use_case.execute(movie_id)
        
        if not movie:
            return jsonify({'error': 'Фильм не найден'}), 404
        
        return jsonify(movie.to_dict())
    finally:
        conn.close()

@movies_bp.route('/', methods=['POST'])
def create_movie():
    """Создать новый фильм"""
    data = request.json
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Название обязательно'}), 400
    
    conn = get_postgres_conn()
    neo4j_driver = get_neo4j_driver()
    
    try:
        movie_repo = PostgresMovieRepository(conn)
        graph_repo = Neo4jGraphRepository(neo4j_driver)
        
        use_case = CreateMovieUseCase(movie_repo, graph_repo)
        movie_id = use_case.execute(
            title=data['title'],
            year=data.get('year', 2000),
            director=data.get('director', 'Unknown'),
            description=data.get('description'),
            actors=data.get('actors', [])
        )
        
        return jsonify({
            'message': 'Фильм создан',
            'id': movie_id
        }), 201
    finally:
        conn.close()
        neo4j_driver.close()

@movies_bp.route('/<string:title>/recommendations', methods=['GET'])
def get_recommendations(title):
    """Получить рекомендации для фильма"""
    limit = request.args.get('limit', 5, type=int)
    
    conn = get_postgres_conn()
    neo4j_driver = get_neo4j_driver()
    
    try:
        movie_repo = PostgresMovieRepository(conn)
        graph_repo = Neo4jGraphRepository(neo4j_driver)
        
        use_case = RecommendMoviesUseCase(graph_repo, movie_repo)
        recommendations = use_case.execute(title, limit)
        
        return jsonify({
            'movie': title,
            'recommendations': recommendations
        })
    finally:
        conn.close()
        neo4j_driver.close()

@movies_bp.route('/<int:movie_id>/actors', methods=['GET'])
def get_movie_actors(movie_id):
    """Получить актёров фильма"""
    conn = get_postgres_conn()
    
    try:
        repo = PostgresMovieRepository(conn)
        movie = repo.get_by_id(movie_id)
        
        if not movie:
            return jsonify({'error': 'Фильм не найден'}), 404
        
        return jsonify({
            'movie_id': movie_id,
            'movie_title': str(movie.title),
            'actors': movie.actors
        })
    finally:
        conn.close()
