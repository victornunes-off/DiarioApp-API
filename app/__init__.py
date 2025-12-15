# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vg211098')
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    # Registra o blueprint de rotas
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Rota raiz para testar se a API está viva
    @app.route('/')
    def index():
        return {"mensagem": "API DiarioApp rodando! Acesse /api/login para testar."}

    return app