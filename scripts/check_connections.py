#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для проверки подключения ко всем базам данных
Запуск: python scripts/check_connections.py
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту, чтобы найти .env
sys.path.append(str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Библиотека python-dotenv не установлена")
    print("Установите: pip install python-dotenv")
    sys.exit(1)

# Загружаем переменные окружения из файла .env в корне проекта
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Загружен файл .env из {env_path}")
else:
    print(f"⚠️ Файл .env не найден по пути {env_path}")
    print("Создайте .env файл на основе .env.example")

def print_status(db_name, success, message=""):
    """Красивый вывод статуса"""
    status = "✅" if success else "❌"
    print(f"{status} {db_name}: {message}")

def check_postgres():
    """Проверка PostgreSQL"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            dbname=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        conn.close()
        print_status('PostgreSQL', True, f'Connected, {version[:50]}...')
    except ImportError:
        print_status('PostgreSQL', False, 'psycopg2 не установлен (pip install psycopg2-binary)')
    except Exception as e:
        print_status('PostgreSQL', False, str(e))

def check_mongodb():
    """Проверка MongoDB"""
    try:
        from pymongo import MongoClient
        client = MongoClient(
            os.getenv('MONGODB_URI', 'mongodb://localhost:27017'),
            serverSelectionTimeoutMS=5000
        )
        client.admin.command('ping')
        db_name = os.getenv('MONGODB_DB', 'cinematch')
        print_status('MongoDB', True, f'Connected to {db_name}')
        client.close()
    except ImportError:
        print_status('MongoDB', False, 'pymongo не установлен (pip install pymongo)')
    except Exception as e:
        print_status('MongoDB', False, str(e))

def check_redis():
    """Проверка Redis"""
    try:
        import redis
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD'),
            socket_connect_timeout=5,
            decode_responses=True
        )
        r.ping()
        # Тестовая запись/чтение
        r.set('test_key', 'test_value', ex=10)
        value = r.get('test_key')
        print_status('Redis', True, f'Connected, test value: {value}')
    except ImportError:
        print_status('Redis', False, 'redis не установлен (pip install redis)')
    except Exception as e:
        print_status('Redis', False, str(e))

def check_qdrant():
    """Проверка Qdrant"""
    try:
        from qdrant_client import QdrantClient

        
        client = QdrantClient(
            host=os.getenv('QDRANT_HOST', 'localhost'),
            port=int(os.getenv('QDRANT_PORT', 6333)),
            api_key=os.getenv('QDRANT_API_KEY'),
            timeout=5,
            https=False,  # Отключаем HTTPS
            prefer_grpc=False  # Используем HTTP
        )
        # Получаем список коллекций
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        print_status('Qdrant', True, f'Connected, collections: {collection_names if collection_names else "нет коллекций"}')
    except ImportError:
        print_status('Qdrant', False, 'qdrant-client не установлен (pip install qdrant-client)')
    except Exception as e:

        print_status('Qdrant', False, str(e))

def check_neo4j():
    """Проверка Neo4j"""
    try:
        from neo4j import GraphDatabase
        
        class Neo4jConnection:
            def __init__(self, uri, user, password):
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                self.driver.verify_connectivity()
                
            def close(self):
                self.driver.close()
        
        conn = Neo4jConnection(
            os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            os.getenv('NEO4J_USER', 'neo4j'),
            os.getenv('NEO4J_PASSWORD', '')
        )
        
        with conn.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            
        conn.close()
        print_status('Neo4j', True, f'Connected, total nodes: {count}')
    except ImportError:
        print_status('Neo4j', False, 'neo4j не установлен (pip install neo4j)')
    except Exception as e:
        print_status('Neo4j', False, str(e))

def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🔌 ПРОВЕРКА ПОДКЛЮЧЕНИЙ К БАЗАМ ДАННЫХ")
    print("="*60 + "\n")
    
    # Проверяем наличие библиотек
    checks = [
        ("PostgreSQL", check_postgres),
        ("MongoDB", check_mongodb),
        ("Redis", check_redis),
        ("Qdrant", check_qdrant),
        ("Neo4j", check_neo4j),
    ]
    
    for name, func in checks:
        print(f"📡 {name}...")
        func()
        print()
    
    print("="*60)
    print("✅ Скрипт завершен")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
