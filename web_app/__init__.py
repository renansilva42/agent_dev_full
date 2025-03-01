# web_app/__init__.py
import os
from flask import Flask
from flask_cors import CORS

def create_app():
    """Cria e configura a aplicação Flask"""
    # Criar aplicação Flask
    app = Flask(__name__, 
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_app', 'static'),
                static_url_path='/static')
    
    # Configurar CORS
    CORS(app)
    
    return app