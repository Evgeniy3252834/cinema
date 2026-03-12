# 🎬 CineMatch — Рекомендательная система фильмов

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://postgresql.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5-green)](https://neo4j.com)
[![Redis](https://img.shields.io/badge/Redis-7-red)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

# 📋 О проекте

**CineMatch** — это учебный проект, демонстрирующий **чистую архитектуру** (Clean Architecture) и **правильное применение паттернов проектирования**. В отличие от избыточных решений, здесь каждый паттерн решает конкретную задачу.

# 🏗️ Архитектура проекта (Clean Architecture)
┌─────────────────────────────────────────────────────────────┐
│ Interfaces (Web/API) │
│ Flask routes │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Application Layer │
│ Use Cases (сценарии использования) │
│ GetMovie, CreateMovie, RecommendMovies │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Domain Layer │
│ Entities (Movie, User, Rating) │
│ Value Objects (MovieTitle, Year, Email) │
│ Repository Interfaces │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Infrastructure Layer │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ PostgreSQL │ │ Neo4j │ │ Redis │ │
│ │ Repository │ │ Graph │ │ Cache │ │
│ │ Implementations│ │ Repository │ │ │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘

# 🗄️ Используемые базы данных

| База данных | Назначение | Почему выбрана? |
|-------------|------------|-----------------|
| **PostgreSQL** | Хранение фильмов, пользователей, оценок | ACID, целостность данных, связи между таблицами |
| **Neo4j** | Граф связей (актёры, режиссёры) | Идеально для рекомендаций через общих актёров |
| **Redis** | Кэширование и счётчики просмотров | Скорость, in-memory, TTL для временных данных |

# 📁 Структура проекта (чистая архитектура)
cinema/
├── src/
│ ├── domain/ # Ядро предметной области
│ │ ├── entities/ # Movie, User, Rating
│ │ │ ├── movie.py
│ │ │ ├── user.py
│ │ │ └── rating.py
│ │ ├── value_objects/ # MovieTitle, Year, Email
│ │ │ ├── movie_title.py
│ │ │ ├── year.py
│ │ │ └── email.py
│ │ └── interfaces/ # Абстракции
│ │ └── repositories/ # IMovieRepository, IUserRepository
│ │ ├── movie_repository.py
│ │ └── user_repository.py
│ ├── application/ # Сценарии использования
│ │ └── use_cases/ # GetMovie, CreateMovie, RecommendMovies
│ │ ├── get_movie.py
│ │ ├── create_movie.py
│ │ └── recommend_movies.py
│ ├── infrastructure/ # Технические детали
│ │ ├── database/ # Подключения к БД
│ │ │ ├── postgres/
│ │ │ │ └── repositories/ # Реализации репозиториев
│ │ │ │ └── postgres_movie_repository.py
│ │ │ ├── neo4j/
│ │ │ │ └── repositories/
│ │ │ │ └── neo4j_graph_repository.py
│ │ │ └── redis/
│ │ │ └── redis_cache.py
│ │ └── cache/ # Кэширование
│ └── interfaces/ # Внешний мир
│ └── web/ # Flask API
│ ├── app.py
│ └── routes/
│ └── movies.py
├── tests/ # Тесты
├── docker-compose.yml # PostgreSQL, Neo4j, Redis
├── init.sql # Инициализация БД
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

# 🚀 Быстрый старт

## Требования
- Python 3.9+
- Docker и Docker Compose
- Git

# Установка и запуск

## 1. Клонируем репозиторий
git clone https://github.com/Evgeniy3252834/cinema.git
cd cinema

## 2. Создаём виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
## или
venv\Scripts\activate     # Windows

## 3. Устанавливаем зависимости
pip install -r requirements.txt

## 4. Создаём файл с переменными окружения
cp .env.example .env
# Отредактируйте .env под свои параметры

## 5. Запускаем базы данных через Docker
docker-compose up -d

## 6. Инициализируем PostgreSQL
docker cp init.sql cinematch-postgres:/init.sql
docker exec -it cinematch-postgres psql -U postgres -d cinematch -f /init.sql

## 7. Запускаем приложение
python -m src.interfaces.web.app
API будет доступно по адресу: http://localhost:5000

# 📡 API Endpoints
Метод	Endpoint	Описание	Используемые БД
GET	/health	Проверка здоровья	-
GET	/api/movies/	Все фильмы	PostgreSQL + Redis (кэш)
GET	/api/movies/<id>	Детали фильма	PostgreSQL + Redis
POST	/api/movies/	Создать фильм	PostgreSQL + Neo4j
GET	/api/movies/<id>/actors	Актёры фильма	PostgreSQL
GET	/api/movies/<title>/recommendations	Рекомендации	Neo4j + PostgreSQL
GET	/api/movies/actors/<name>/movies	Фильмы актёра	Neo4j

# 🧪 Примеры запросов
## Получить все фильмы
curl http://localhost:5000/api/movies/

## Получить конкретный фильм
curl http://localhost:5000/api/movies/1

## Создать новый фильм (сохраняется в PostgreSQL и Neo4j)
curl -X POST http://localhost:5000/api/movies/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Inception",
    "year": 2010,
    "director": "Christopher Nolan",
    "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"]
  }'

## Получить рекомендации для фильма (через Neo4j)
curl http://localhost:5000/api/movies/Inception/recommendations?limit=5

## Получить актёров фильма
curl http://localhost:5000/api/movies/1/actors

# 📊 Схема данных в Neo4j (для рекомендаций)
(Actor: {name: "Leonardo DiCaprio"})-[:ACTED_IN]->(Movie: {title: "Inception"})
(Director: {name: "Christopher Nolan"})-[:DIRECTED]->(Movie: {title: "Inception"})

Рекомендации строятся через:
- Общих актёров: "Если вам понравился фильм X с актёром Y, посмотрите другие фильмы с Y"
- Того же режиссёра: "Посмотрите другие фильмы этого режиссёра"

# 📄 Лицензия
MIT License — свободно используйте для обучения и разработки.

# 👨‍💻 Авторы
Овчинников Евгений, Михайлов Сергей — учебный проект по курсу "Архитектура ПО"

⭐ Если проект полезен, поставьте звезду на GitHub!
