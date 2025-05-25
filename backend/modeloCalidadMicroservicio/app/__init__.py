from flask import Flask
from backend.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes import modelo_routes
    app.register_blueprint(modelo_routes, url_prefix='/modelo')

    return app