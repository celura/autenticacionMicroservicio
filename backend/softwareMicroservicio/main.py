import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.models import db
from app.routes import software_routes
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY

    db.init_app(app)
    JWTManager(app)
    with app.app_context():
        db.create_all() 

    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    app.register_blueprint(software_routes, url_prefix='/software')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
