
## 🗄️ Базы данных

| База данных | Назначение | Почему именно она? |
|------------|------------|-------------------|
| **PostgreSQL** | Пользователи, фильмы, оценки | ACID, целостность данных, сложные запросы с JOIN |
| **MongoDB** | Логи действий, события | Гибкая схема, быстрое хранение JSON-документов |
| **Redis** | Кэш, сессии, счётчики | In-memory, скорость, TTL для временных данных |
| **Qdrant** | Векторные эмбеддинги фильмов | Поиск по семантическому сходству |
| **Neo4j** | Связи актёр-фильм-режиссёр | Графовые запросы, обход связей за O(1) |

## 🚀 Быстрый старт

### Требования
- Python 3.9+
- Docker и Docker Compose
- Git

### Установка и запуск

```bash
# 1. Клонируем репозиторий
git clone https://github.com/Evgeniy3252834/cinema.git
cd cinema

# 2. Создаём виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# 3. Устанавливаем зависимости
pip install -r requirements.txt

# 4. Создаём файл с переменными окружения
cp .env.example .env
# Отредактируйте .env под свои параметры

# 5. Запускаем все базы данных одной командой
docker-compose up -d

# 6. Инициализируем базу данных (таблицы и тестовые данные)
docker exec -it cinematch-postgres psql -U postgres -d cinematch -f init.sql

# 7. Запускаем API
python app.py

API будет доступно по адресу: http://localhost:5000

📡 API Endpoints
Метод	Endpoint	Описание
GET	/	Информация о проекте
GET	/health	Проверка статуса всех БД
GET	/movies	Список всех фильмов (с кэшированием в Redis)
GET	/movies/<id>	Детальная информация о фильме
GET	/movies/top	Топ-5 фильмов по оценкам
GET	/rate/<user_id>/<movie_id>/<rating>	Поставить оценку фильму
🧪 Примеры запросов
bash
# Получить все фильмы
curl http://localhost:5000/movies

# Поставить оценку
curl http://localhost:5000/rate/1/5/10

# Проверить здоровье сервиса
curl http://localhost:5000/health
📦 Структура проекта
text
cinema/
├── app.py                 # Основное Flask приложение
├── requirements.txt       # Зависимости Python
├── docker-compose.yml     # Запуск всех БД одной командой
├── init.sql               # SQL для инициализации PostgreSQL
├── .env.example           # Шаблон переменных окружения
├── .gitignore             # Игнорируемые файлы
├── README.md              # Документация
├── scripts/               # Вспомогательные скрипты
│   └── check_connections.py
├── docs/                  # Документация (пусто)
└── services/              # Микросервисы (пусто)
🔄 Планы по развитию
Интеграция с Qdrant (векторные рекомендации)

Интеграция с Neo4j (графовые запросы)

Добавление RabbitMQ для фоновых задач

JWT авторизация

Web-интерфейс на React/Vue

🛠️ Технологии
Backend: Python, Flask

Databases: PostgreSQL, MongoDB, Redis, Qdrant, Neo4j

DevOps: Docker, Docker Compose

Version Control: Git, GitHub

📄 Лицензия
MIT License — свободно используйте для обучения и разработки.

👨‍💻 Автор
Евгений — учебный проект для демонстрации полиглотной архитектуры баз данных.

⭐ Если проект полезен, поставьте звезду на GitHub!
