"""Модели данных для фильмов"""

class Movie:
    """Модель фильма для PostgreSQL"""
    
    def __init__(self, id=None, title=None, year=None, director=None, 
                 description=None, imdb_rating=None):
        self.id = id
        self.title = title
        self.year = year
        self.director = director
        self.description = description
        self.imdb_rating = imdb_rating
    
    @classmethod
    def from_db_row(cls, row):
        """Создать объект из строки БД"""
        return cls(
            id=row[0],
            title=row[1],
            year=row[2],
            director=row[3],
            description=row[4],
            imdb_rating=float(row[5]) if row[5] else None
        )
    
    def to_dict(self):
        """Преобразовать в словарь для JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'director': self.director,
            'description': self.description,
            'imdb_rating': self.imdb_rating
        }


class ActorNode:
    """Узел актёра для Neo4j"""
    
    def __init__(self, name, born=None, movie_title=None):
        self.name = name
        self.born = born
        self.movie_title = movie_title
    
    @classmethod
    def from_neo4j_node(cls, node):
        """Создать из узла Neo4j"""
        return cls(
            name=node.get('name'),
            born=node.get('born'),
            movie_title=node.get('movie_title')
        )
