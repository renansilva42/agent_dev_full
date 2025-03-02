# config/config_manager.py
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    """Gerencia as configurações da aplicação."""
    
    def __init__(self, config_file=None, env_file=None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file (str, optional): Caminho para o arquivo de configuração JSON.
            env_file (str, optional): Caminho para o arquivo .env.
        """
        self.logger = logging.getLogger(__name__)
        self.config = {}
        
        # Carregar variáveis de ambiente do arquivo .env
        if env_file:
            env_path = Path(env_file)
        else:
            env_path = Path('.env')
        
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            self.logger.info(f"Variáveis de ambiente carregadas de {env_path}")
        else:
            self.logger.warning(f"Arquivo .env não encontrado em {env_path}")
        
        # Carregar configurações do arquivo JSON
        if config_file:
            config_path = Path(config_file)
        else:
            config_path = Path('config/config.json')
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                self.logger.info(f"Configurações carregadas de {config_path}")
            except Exception as e:
                self.logger.error(f"Erro ao carregar configurações de {config_path}: {str(e)}")
        else:
            self.logger.warning(f"Arquivo de configuração não encontrado em {config_path}")
    
    def get(self, key, default=None):
        """
        Obtém um valor de configuração.
        
        Args:
            key (str): Chave da configuração.
            default: Valor padrão caso a chave não exista.
            
        Returns:
            O valor da configuração ou o valor padrão.
        """
        # Primeiro, verificar variáveis de ambiente
        env_key = key.upper()
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
        
        # Em seguida, verificar no arquivo de configuração
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Define um valor de configuração.
        
        Args:
            key (str): Chave da configuração.
            value: Valor da configuração.
        """
        self.config[key] = value
    
    def save(self, config_file=None):
        """
        Salva as configurações em um arquivo JSON.
        
        Args:
            config_file (str, optional): Caminho para o arquivo de configuração JSON.
        """
        if config_file:
            config_path = Path(config_file)
        else:
            config_path = Path('config/config.json')
        
        try:
            # Garantir que o diretório exista
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info(f"Configurações salvas em {config_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações em {config_path}: {str(e)}")