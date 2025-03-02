# main.py
import os
import logging
from pathlib import Path
from flask import Flask
from flask_login import LoginManager

from config.config_manager import ConfigManager
from model.transformer_model import TransformerModel
from agents.base_agent import BaseAgent
from agents.code_analysis_agent import CodeAnalysisAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.database_agent import DatabaseAgent
from agents.devops_agent import DevOpsAgent
from agents.project_improvement_agent import ProjectImprovementAgent
from agents.project_management_agent import ProjectManagementAgent
from agents.request_analyzer_agent import RequestAnalyzerAgent
from agents.response_optimizer_agent import ResponseOptimizerAgent
from integration.integration_layer import IntegrationLayer
from database import db, init_db
from models.user import User

# Configuração de login
login_manager = LoginManager()

def setup_logging():
    """Configura o sistema de logging"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Criar handler para arquivo
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)
    
    # Criar handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Definir formato
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def create_flask_app():
    """Cria a aplicação Flask"""
    app = Flask(__name__, 
                template_folder='web_app/templates',
                static_folder='static')
    return app

def configure_routes(app, integration_layer):
    """Configura as rotas da aplicação"""
    from web_app.routes import routes
    from web_app.api import api
    
    # Registrar blueprints
    app.register_blueprint(routes)
    app.register_blueprint(api)
    
    # Adicionar integration_layer à configuração da aplicação
    app.config['INTEGRATION_LAYER'] = integration_layer

def create_app():
    """Cria e configura a aplicação Flask"""
    try:
        # Inicializar logging
        logger = setup_logging()
        logger.info("Iniciando configuração da aplicação")
        
        # Carregar configurações
        config_manager = ConfigManager()
        
        # Criar aplicação Flask
        app = create_flask_app()
        
        # Configurar banco de dados
        app.config['SQLALCHEMY_DATABASE_URI'] = config_manager.get('database_uri', 'sqlite:///app.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Inicializar banco de dados
        init_db(app)
        
        # Inicializar login manager
        login_manager.init_app(app)
        login_manager.login_view = 'routes.login'
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Configurar chave secreta
        app.secret_key = config_manager.get('flask_secret_key')
        
        # Atualizar configurações da aplicação
        app.config.update(
            SESSION_TYPE='filesystem',
            SESSION_PERMANENT=False,
            SESSION_USE_SIGNER=True,
            DEBUG=config_manager.get('debug'),
            UPLOAD_FOLDER=config_manager.get('upload_folder', 'uploads')
        )
        
        # Inicializar modelo
        model = TransformerModel()
        
        # Inicializar agentes
        code_analysis_agent = CodeAnalysisAgent(model)
        backend_agent = BackendAgent(model)
        frontend_agent = FrontendAgent(model)
        database_agent = DatabaseAgent(model)
        devops_agent = DevOpsAgent(model)
        project_improvement_agent = ProjectImprovementAgent(model)
        project_management_agent = ProjectManagementAgent(model)
        request_analyzer_agent = RequestAnalyzerAgent(model)
        response_optimizer_agent = ResponseOptimizerAgent(model)
        
        # Criar camada de integração
        integration_layer = IntegrationLayer(
            code_analysis_agent=code_analysis_agent,
            backend_agent=backend_agent,
            frontend_agent=frontend_agent,
            database_agent=database_agent,
            devops_agent=devops_agent,
            project_improvement_agent=project_improvement_agent,
            project_management_agent=project_management_agent,
            request_analyzer_agent=request_analyzer_agent,
            response_optimizer_agent=response_optimizer_agent
        )
        
        # Configurar rotas
        configure_routes(app, integration_layer)
        
        # Criar tabelas do banco de dados
        with app.app_context():
            db.create_all()
        
        return app
        
    except Exception as e:
        logger.error(f"Erro ao configurar aplicação: {str(e)}")
        raise

def run_app():
    """Executa a aplicação Flask"""
    try:
        # Criar e configurar a aplicação
        app = create_app()
        
        # Obter configurações
        config_manager = ConfigManager()
        host = config_manager.get('host', '0.0.0.0')
        port = config_manager.get('port', 5000)
        debug = config_manager.get('debug', False)
        
        # Executar aplicação
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao executar aplicação: {str(e)}")
        raise

if __name__ == "__main__":
    run_app()