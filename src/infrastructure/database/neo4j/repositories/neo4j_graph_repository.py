"""Репозиторий для графовых запросов в Neo4j"""
from typing import List, Dict
from neo4j import GraphDatabase

class Neo4jGraphRepository:
    """Работа с графом фильмов для рекомендаций"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def add_movie(self, title: str, year: int, director: str):
        """Добавить фильм в граф"""
        with self.driver.session() as session:
            session.run("""
                MERGE (m:Movie {title: $title, year: $year})
                MERGE (d:Director {name: $director})
                MERGE (d)-[:DIRECTED]->(m)
            """, title=title, year=year, director=director)
    
    def add_actor(self, movie_title: str, actor_name: str):
        """Добавить актёра к фильму"""
        with self.driver.session() as session:
            session.run("""
                MATCH (m:Movie {title: $movie_title})
                MERGE (a:Actor {name: $actor_name})
                MERGE (a)-[:ACTED_IN]->(m)
            """, movie_title=movie_title, actor_name=actor_name)
    
    def get_recommendations_by_actors(self, movie_title: str, limit: int = 5) -> List[Dict]:
        """Рекомендации через общих актёров"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Movie {title: $movie_title})<-[:ACTED_IN]-(a:Actor)
                MATCH (a)-[:ACTED_IN]->(rec:Movie)
                WHERE rec.title <> $movie_title
                RETURN rec.title as title, COUNT(a) as common_actors
                ORDER BY common_actors DESC
                LIMIT $limit
            """, movie_title=movie_title, limit=limit)
            return [dict(record) for record in result]
    
    def get_recommendations_by_director(self, movie_title: str, limit: int = 5) -> List[Dict]:
        """Рекомендации через режиссёра"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Movie {title: $movie_title})<-[:DIRECTED]-(d:Director)
                MATCH (d)-[:DIRECTED]->(rec:Movie)
                WHERE rec.title <> $movie_title
                RETURN rec.title as title
                LIMIT $limit
            """, movie_title=movie_title, limit=limit)
            return [dict(record) for record in result]
    
    def get_recommendations_by_genre(self, genre: str, limit: int = 5) -> List[Dict]:
        """Рекомендации по жанру"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre {name: $genre})
                RETURN m.title as title, m.year as year
                ORDER BY m.year DESC
                LIMIT $limit
            """, genre=genre, limit=limit)
            return [dict(record) for record in result]
