import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.models import db
from app.routes import modelo_routes
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    with app.app_context():
        db.create_all() 
        
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
    app.register_blueprint(modelo_routes, url_prefix='/modelo')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5002)
