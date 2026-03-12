-- Таблица фильмов
CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    director VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица актёров
CREATE TABLE IF NOT EXISTS movie_actors (
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    actor_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (movie_id, actor_name)
);

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица оценок
CREATE TABLE IF NOT EXISTS ratings (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 10),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, movie_id)
);

-- Индексы для скорости
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movie_actors_movie_id ON movie_actors(movie_id);
CREATE INDEX idx_ratings_movie_id ON ratings(movie_id);

-- Тестовые данные
INSERT INTO movies (title, year, director, description) VALUES
('The Matrix', 1999, 'Lana Wachowski', 'A computer hacker learns about the true nature of reality'),
('Inception', 2010, 'Christopher Nolan', 'A thief who steals corporate secrets through dream-sharing technology'),
('Interstellar', 2014, 'Christopher Nolan', 'A team of explorers travel through a wormhole in space'),
('Pulp Fiction', 1994, 'Quentin Tarantino', 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine'),
('Fight Club', 1999, 'David Fincher', 'An insomniac office worker and a devilish soap maker form an underground fight club')
ON CONFLICT (title) DO NOTHING;

-- Получаем ID фильмов для вставки актёров
DO $$
DECLARE
    matrix_id INT;
    inception_id INT;
    interstellar_id INT;
    pulp_id INT;
    fight_id INT;
BEGIN
    SELECT id INTO matrix_id FROM movies WHERE title = 'The Matrix';
    SELECT id INTO inception_id FROM movies WHERE title = 'Inception';
    SELECT id INTO interstellar_id FROM movies WHERE title = 'Interstellar';
    SELECT id INTO pulp_id FROM movies WHERE title = 'Pulp Fiction';
    SELECT id INTO fight_id FROM movies WHERE title = 'Fight Club';

    -- Вставляем актёров
    INSERT INTO movie_actors (movie_id, actor_name) VALUES
    (matrix_id, 'Keanu Reeves'), (matrix_id, 'Laurence Fishburne'), (matrix_id, 'Carrie-Anne Moss'),
    (inception_id, 'Leonardo DiCaprio'), (inception_id, 'Joseph Gordon-Levitt'), (inception_id, 'Elliot Page'),
    (interstellar_id, 'Matthew McConaughey'), (interstellar_id, 'Anne Hathaway'), (interstellar_id, 'Jessica Chastain'),
    (pulp_id, 'John Travolta'), (pulp_id, 'Uma Thurman'), (pulp_id, 'Samuel L. Jackson'),
    (fight_id, 'Brad Pitt'), (fight_id, 'Edward Norton'), (fight_id, 'Helena Bonham Carter')
    ON CONFLICT DO NOTHING;
END $$;

-- Тестовый пользователь
INSERT INTO users (username, email) VALUES
('test_user', 'test@example.com')
ON CONFLICT DO NOTHING;

-- Проверяем, что добавилось
SELECT 'Movies count: ' || COUNT(*) FROM movies;
SELECT 'Actors count: ' || COUNT(*) FROM movie_actors;
SELECT 'Users count: ' || COUNT(*) FROM users;
