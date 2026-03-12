"""Сервис для работы с Neo4j (граф связей)"""
from neo4j import GraphDatabase
import os

class Neo4jService:
    """Работа с графовой БД"""
    
    def __init__(self):
        self.driver = None
        self.connect()
    
    def connect(self):
        """Подключение к Neo4j"""
        self.driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI'),
            auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
        )
    
    def close(self):
        """Закрыть соединение"""
        if self.driver:
            self.driver.close()
    
    def add_movie_with_actors(self, movie_title, year, director, actors):
        """Добавить фильм с актёрами в граф"""
        with self.driver.session() as session:
            # Создаём фильм и режиссёра
            session.run("""
                MERGE (m:Movie {title: $title, year: $year})
                MERGE (d:Director {name: $director})
                MERGE (d)-[:DIRECTED]->(m)
            """, title=movie_title, year=year, director=director)
            
            # Добавляем актёров
            for actor in actors:
                session.run("""
                    MATCH (m:Movie {title: $title})
                    MERGE (a:Actor {name: $actor_name})
                    MERGE (a)-[:ACTED_IN]->(m)
                """, title=movie_title, actor_name=actor)
    
    def get_actors_by_movie(self, movie_title):
        """Получить всех актёров фильма"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Actor)-[:ACTED_IN]->(m:Movie {title: $title})
                RETURN a.name as actor_name
            """, title=movie_title)
            return [record['actor_name'] for record in result]
    
    def get_movies_by_actor(self, actor_name):
        """Получить все фильмы актёра"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Actor {name: $name})-[:ACTED_IN]->(m:Movie)
                RETURN m.title as movie_title, m.year as year
            """, name=actor_name)
            return [dict(record) for record in result]
    
    def get_movies_by_director(self, director_name):
        """Получить все фильмы режиссёра"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Director {name: $name})-[:DIRECTED]->(m:Movie)
                RETURN m.title as movie_title, m.year as year
            """, name=director_name)
            return [dict(record) for record in result]
    
    def get_common_actors(self, movie1_title, movie2_title):
        """Найти общих актёров в двух фильмах"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Actor)-[:ACTED_IN]->(m1:Movie {title: $movie1})
                WHERE (a)-[:ACTED_IN]->(m2:Movie {title: $movie2})
                RETURN a.name as actor_name
            """, movie1=movie1_title, movie2=movie2_title)
            return [record['actor_name'] for record in result]
