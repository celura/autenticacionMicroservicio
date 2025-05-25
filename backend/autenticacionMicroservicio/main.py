import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.models import db
from app.routes import auth_routes
from flask_cors import CORS 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    with app.app_context():
        db.create_all() 
    CORS(app, origins="https://calidad-servidor-front.vercel.app", supports_credentials=True)

    app.register_blueprint(auth_routes, url_prefix='/auth')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5001)
