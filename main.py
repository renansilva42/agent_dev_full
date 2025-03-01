# main.py

import os
import logging
from flask import Flask, send_from_directory
from dotenv import load_dotenv
from model.transformer_model import TransformerModel
from integration.integration_layer import IntegrationLayer
from agents.code_analysis_agent import CodeAnalysisAgent
from agents.project_improvement_agent import ProjectImprovementAgent
from agents.database_agent import DatabaseAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.devops_agent import DevOpsAgent
from agents.project_management_agent import ProjectManagementAgent
from agents.response_optimizer_agent import ResponseOptimizerAgent
from agents.request_analyzer_agent import RequestAnalyzerAgent
from web_app.routes import configure_routes
from web_app import create_app as create_flask_app

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    
    # Set up logging
    logger = setup_logging()
    
    # Load environment variables
    load_dotenv()
    
    # Create Flask app with proper static file configuration
    app = create_flask_app()
    
    # Configure secret key for sessions
    secret_key = os.getenv('FLASK_SECRET_KEY')
    if not secret_key:
        secret_key = os.urandom(24).hex()
        logger.warning("No FLASK_SECRET_KEY found in .env, using generated key")
    app.secret_key = secret_key
    
    # Configure Flask app
    app.config.update(
        SEND_FILE_MAX_AGE_DEFAULT=0,  # Disable caching for development
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        SESSION_COOKIE_SECURE=False,  # Allow non-HTTPS for development
        SESSION_COOKIE_HTTPONLY=True,  # Protect session cookie
        PERMANENT_SESSION_LIFETIME=1800  # 30 minutes session lifetime
    )
    
    try:
        # Initialize the transformer model
        transformer_model = TransformerModel()
        
        # Initialize request analyzer first
        request_analyzer_agent = RequestAnalyzerAgent(transformer_model)
        
        # Initialize all other agents
        code_analysis_agent = CodeAnalysisAgent(transformer_model)
        project_improvement_agent = ProjectImprovementAgent(transformer_model)
        database_agent = DatabaseAgent(transformer_model)
        backend_agent = BackendAgent(transformer_model)
        frontend_agent = FrontendAgent(transformer_model)
        devops_agent = DevOpsAgent(transformer_model)
        project_management_agent = ProjectManagementAgent(transformer_model)
        response_optimizer_agent = ResponseOptimizerAgent(transformer_model)
        
        # Initialize integration layer with all agents
        integration_layer = IntegrationLayer(
            code_analysis_agent=code_analysis_agent,
            project_improvement_agent=project_improvement_agent,
            database_agent=database_agent,
            backend_agent=backend_agent,
            frontend_agent=frontend_agent,
            devops_agent=devops_agent,
            project_management_agent=project_management_agent,
            response_optimizer_agent=response_optimizer_agent,
            request_analyzer_agent=request_analyzer_agent
        )
        
        # Configure routes
        configure_routes(app, integration_layer)
        
        # Log application setup information
        logger.info("Application setup completed successfully")
        logger.info("All agents initialized and ready")
        
        return app
        
    except Exception as e:
        logger.error(f"Error initializing application: {str(e)}")
        raise

def main():
    """Run the Flask application"""
    try:
        app = create_app()
        # Enable debug mode for development
        app.debug = True
        # Run the application
        app.run(host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
