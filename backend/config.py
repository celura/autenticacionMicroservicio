import os
from datetime import timedelta
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:proyectoCalidadServidor@localhost/calidad_servidor'  
    SQLALCHEMY_TRACK_MODIFICATIONS = False