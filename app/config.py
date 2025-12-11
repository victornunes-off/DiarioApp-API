# app/config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-temporaria-muito-ruim'

 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Opcional: deixa ainda mais claro que é obrigatório
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError(
            "Variável de ambiente DATABASE_URL não encontrada! "
            "Configure no arquivo .env ou na variável de ambiente."
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False