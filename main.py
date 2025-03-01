# main.py
import os
import logging
from flask import Flask, send_from_directory
from dotenv import load_dotenv

# Importar gerenciador de configuração
from config.config_manager import ConfigManager

# Importar factory de agentes
from agents.agent_factory import AgentFactory

# Importar modelo
from model.transformer_model import TransformerModel

# Importar camada de integração
from integration.integration_layer import IntegrationLayer

# Importar configuração de rotas
from web_app.routes import configure_routes
from web_app import create_app as create_flask_app

def setup_logging():
    """Configura o sistema de logging"""
    logger = logging.getLogger(__name__)
    return logger

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
        
        # Configurar chave secreta
        app.secret_key = config_manager.get('flask_secret_key')
        
        # Atualizar configurações da aplicação
        app.config.update(
            SESSION_TYPE='filesystem',
            SESSION_PERMANENT=False,
            SESSION_USE_SIGNER=True,
            DEBUG=config_manager.get('debug')
        )
        
        # Inicializar modelo
        model = TransformerModel()
        
        # Criar factory de agentes
        agent_factory = AgentFactory(model)
        
        # Inicializar agentes
        agents = {
            'code_analysis': agent_factory.create_agent('code_analysis'),
            'project_improvement': agent_factory.create_agent('project_improvement'),
            'database': agent_factory.create_agent('database'),
            'backend': agent_factory.create_agent('backend'),
            'frontend': agent_factory.create_agent('frontend'),
            'devops': agent_factory.create_agent('devops'),
            'project_management': agent_factory.create_agent('project_management'),
        }
        
        # Inicializar agentes especiais
        response_optimizer = agent_factory.create_agent('response_optimizer')
        request_analyzer = agent_factory.create_agent('request_analyzer')
        
        # Criar camada de integração
        integration_layer = IntegrationLayer(
            code_analysis_agent=agents['code_analysis'],
            project_improvement_agent=agents['project_improvement'],
            database_agent=agents['database'],
            backend_agent=agents['backend'],
            frontend_agent=agents['frontend'],
            devops_agent=agents['devops'],
            project_management_agent=agents['project_management'],
            response_optimizer_agent=response_optimizer,
            request_analyzer_agent=request_analyzer
        )
        
        # Configurar rotas
        configure_routes(app, integration_layer)
        
        # Registrar informações de inicialização
        logger.info("Aplicação configurada com sucesso")
        logger.info("Todos os agentes inicializados e prontos")
        
        return app
        
    except Exception as e:
        logger.error(f"Erro ao inicializar aplicação: {str(e)}")
        raise

def main():
    """Executa a aplicação Flask"""
    try:
        # Criar e configurar a aplicação
        app = create_app()
        
        # Obter configurações
        config_manager = ConfigManager()
        host = config_manager.get('host', '0.0.0.0')
        port = config_manager.get('port', 5000)
        debug = config_manager.get('debug', False)
        
        # Executar a aplicação
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        print(f"Falha ao iniciar aplicação: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()