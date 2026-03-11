from flask import Flask, jsonify, request
import psycopg2
import redis
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)

def get_postgres():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def get_redis():
    return redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        decode_responses=True
    )

def get_mongo():
    client = MongoClient(os.getenv('MONGODB_URI'))
    return client[os.getenv('MONGODB_DB')]

@app.route('/')
def home():
    return jsonify({
        'project': 'CineMatch',
        'status': 'running',
        'endpoints': [
            '/health',
            '/movies',
            '/movies/<id>',
            '/movies/top',
            '/rate/<user_id>/<movie_id>/<int:rating>'
        ]
    })

@app.route('/health')
def health():
    status = {
        'postgres': False,
        'redis': False,
        'mongodb': False
    }
    
    try:
        pg = get_postgres()
        pg.close()
        status['postgres'] = True
    except:
        pass
    
    try:
        r = get_redis()
        r.ping()
        status['redis'] = True
    except:
        pass
    
    try:
        mongo = get_mongo()
        mongo.command('ping')
        status['mongodb'] = True
    except:
        pass
    
    return jsonify(status)

@app.route('/movies')
def get_movies():

    r = get_redis()
    cached = r.get('all_movies')
    if cached:
        return jsonify({
            'source': 'redis',
            'movies': json.loads(cached)
        })
    
    conn = get_postgres()
    cur = conn.cursor()
    cur.execute('SELECT id, title, year, director, imdb_rating FROM movies ORDER BY id')
    movies = []
    for row in cur.fetchall():
        movies.append({
            'id': row[0],
            'title': row[1],
            'year': row[2],
            'director': row[3],
            'rating': float(row[4]) if row[4] else None
        })
    cur.close()
    conn.close()
    

    r.setex('all_movies', 60, json.dumps(movies))
    

    try:
        mongo = get_mongo()
        mongo.logs.insert_one({
            'endpoint': '/movies',
            'timestamp': '2026-03-11',
            'user_agent': request.headers.get('User-Agent')
        })
    except:
        pass
    
    return jsonify({
        'source': 'postgresql',
        'movies': movies
    })

@app.route('/movies/<int:movie_id>')
def get_movie(movie_id):
    conn = get_postgres()
    cur = conn.cursor()
    cur.execute('SELECT id, title, year, director, description, imdb_rating FROM movies WHERE id = %s', (movie_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        return jsonify({
            'id': row[0],
            'title': row[1],
            'year': row[2],
            'director': row[3],
            'description': row[4],
            'rating': float(row[5]) if row[5] else None
        })
    return jsonify({'error': 'Movie not found'}), 404

@app.route('/movies/top')
def top_movies():
    conn = get_postgres()
    cur = conn.cursor()
    cur.execute('''
        SELECT m.id, m.title, m.year, m.director, AVG(r.rating) as avg_rating
        FROM movies m
        LEFT JOIN ratings r ON m.id = r.movie_id
        GROUP BY m.id
        ORDER BY avg_rating DESC NULLS LAST
        LIMIT 5
    ''')
    movies = []
    for row in cur.fetchall():
        movies.append({
            'id': row[0],
            'title': row[1],
            'year': row[2],
            'director': row[3],
            'avg_rating': float(row[4]) if row[4] else None
        })
    cur.close()
    conn.close()
    return jsonify(movies)

@app.route('/rate/<int:user_id>/<int:movie_id>/<int:rating>')
def rate_movie(user_id, movie_id, rating):
    if rating < 1 or rating > 10:
        return jsonify({'error': 'Rating must be between 1 and 10'}), 400
    
    conn = get_postgres()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO ratings (user_id, movie_id, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, movie_id) 
            DO UPDATE SET rating = EXCLUDED.rating
        ''', (user_id, movie_id, rating))
        conn.commit()
        

        r = get_redis()
        r.delete('all_movies')
        
        return jsonify({'success': True, 'message': 'Rating saved'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    print("🚀 Запуск CineMatch API...")
    print("📡 PostgreSQL:", os.getenv('POSTGRES_HOST'))
    print("📡 Redis:", os.getenv('REDIS_HOST'))
    print("📡 MongoDB:", os.getenv('MONGODB_URI'))
    print("\n🌐 API доступно на http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
