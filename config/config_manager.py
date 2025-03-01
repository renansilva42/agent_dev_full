# config/config_manager.py
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigManager:
    """Singleton para gerenciamento de configurações"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Configurações padrão
        self.config = {
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'openai_model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
            'max_input_tokens': int(os.getenv('MAX_INPUT_TOKENS', '4000')),
            'chunk_size': int(os.getenv('CHUNK_SIZE', '2000')),
            'debug': os.getenv('DEBUG', 'False').lower() == 'true',
            'flask_secret_key': os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex()),
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', '5000')),
        }
        
        # Configurar logging
        self._setup_logging()
        
        self._initialized = True
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        log_level = logging.DEBUG if self.config['debug'] else logging.INFO
        
        # Configuração básica
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ]
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Define um valor de configuração"""
        self.config[key] = value