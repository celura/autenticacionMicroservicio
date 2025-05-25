from flask import Flask
from app.routes import riesgo_routes
from backend.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(riesgo_routes, url_prefix='/riesgo')

    return app