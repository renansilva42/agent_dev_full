# database.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)
    migrate.init_app(app, db)