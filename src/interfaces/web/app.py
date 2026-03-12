"""Flask приложение"""
from flask import Flask, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """Фабрика приложений"""
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    

    # Регистрируем blueprints
    from src.interfaces.web.routes.movies import movies_bp
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
