"""Use Case: Рекомендации фильмов"""
from typing import List, Dict
from ...infrastructure.database.neo4j.repositories.neo4j_graph_repository import Neo4jGraphRepository
from ...domain.interfaces.repositories.movie_repository import MovieRepository

class RecommendMoviesUseCase:
    """Сценарий получения рекомендаций"""
    
    def __init__(self, 
                 graph_repo: Neo4jGraphRepository,
                 movie_repo: MovieRepository):
        self.graph_repo = graph_repo
        self.movie_repo = movie_repo
    
    def execute(self, movie_title: str, limit: int = 5) -> List[Dict]:
        """Получить рекомендации на основе графа"""
        
        # 1. Рекомендации через общих актёров
        by_actors = self.graph_repo.get_recommendations_by_actors(movie_title, limit)
        
        # 2. Рекомендации через режиссёра
        by_director = self.graph_repo.get_recommendations_by_director(movie_title, limit)
        
        # 3. Объединяем и ранжируем
        recommendations = {}
        
        for rec in by_actors:
            recommendations[rec['title']] = {
                'title': rec['title'],
                'score': rec['common_actors'] * 2,
                'reason': 'common_actors'
            }
        
        for rec in by_director:
            if rec['title'] in recommendations:
                recommendations[rec['title']]['score'] += 3
                recommendations[rec['title']]['reason'] = 'actors_and_director'
            else:
                recommendations[rec['title']] = {
                    'title': rec['title'],
                    'score': 3,
                    'reason': 'same_director'
                }
        
        # 4. Сортируем по убыванию score
        sorted_recs = sorted(
            recommendations.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )[:limit]
        
        # 5. Обогащаем данными из PostgreSQL
        result = []
        for rec in sorted_recs:
            movie = self.movie_repo.get_by_title(rec['title'])
            if movie:
                result.append({
                    'id': movie.id,
                    'title': rec['title'],
                    'year': int(movie.year),
                    'director': movie.director,
                    'score': rec['score'],
                    'reason': rec['reason']
                })
        
        return result
