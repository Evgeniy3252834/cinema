#!/usr/bin/env python
"""Movies Microservice - управление фильмами и связями"""

from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import logging
from src.routes.movie_routes import movies_bp

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """Фабрика приложений Flask"""
    app = Flask(__name__)
    
    # Настройки
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Регистрируем Blueprint
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'movies-service',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': [
                'GET /api/movies/',
                'GET /api/movies/<id>',
                'POST /api/movies/',
                'GET /api/movies/<id>/actors',
                'GET /api/movies/actors/<name>/movies'
            ]
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5002))
    print(f"🚀 Movies Service запущен на порту {port}")
    print(f"📡 PostgreSQL: {os.getenv('POSTGRES_HOST')}")
    print(f"📡 Neo4j: {os.getenv('NEO4J_URI')}")
    print(f"📡 Redis: {os.getenv('REDIS_HOST')}")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
