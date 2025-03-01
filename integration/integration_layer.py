# integration/integration_layer.py
import os
import logging
import concurrent.futures
from typing import Dict, List, Optional, Any
from pathlib import Path

class IntegrationError(Exception):
    """Exceção personalizada para erros na camada de integração"""
    pass

class FileManager:
    """Gerencia operações de arquivo centralizadas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_cache = {}
    
    def get_project_files(self, project_path: str) -> List[str]:
        """Obtém lista de arquivos relevantes do projeto"""
        if project_path in self.file_cache:
            return self.file_cache[project_path]['files']
            
        try:
            files = []
            ignored_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.env'}
            relevant_extensions = {'.py', '.js', '.html', '.css', '.json', '.yml', '.yaml', '.md', '.txt'}
            
            path = Path(project_path)
            for item in path.rglob('*'):
                if item.is_file() and not any(part in ignored_dirs for part in item.parts):
                    if item.suffix in relevant_extensions:
                        files.append(str(item.relative_to(path)))
            
            self.file_cache[project_path] = {'files': files}
            self.logger.info(f"Encontrados {len(files)} arquivos relevantes")
            return files
            
        except Exception as e:
            self.logger.error(f"Erro ao obter arquivos do projeto: {str(e)}")
            raise IntegrationError(f"Erro ao obter arquivos do projeto: {str(e)}")
    
    def get_file_content(self, project_path: str, file_path: str) -> str:
        """Obtém conteúdo de um arquivo específico"""
        cache_key = f"{project_path}:{file_path}"
        if cache_key in self.file_cache:
            return self.file_cache[cache_key]['content']
            
        try:
            full_path = Path(project_path) / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.file_cache[cache_key] = {'content': content}
                return content
                
        except Exception as e:
            self.logger.error(f"Erro ao ler arquivo {file_path}: {str(e)}")
            return f"Erro ao ler arquivo: {str(e)}"
    
    def get_files_with_content(self, project_path: str) -> Dict[str, str]:
        """Obtém dicionário de arquivos com seu conteúdo"""
        files = self.get_project_files(project_path)
        result = {}
        
        for file_path in files:
            result[file_path] = self.get_file_content(project_path, file_path)
            
        return result

class IntegrationLayer:
    """Camada de integração que coordena os agentes"""
    
    def __init__(self, code_analysis_agent, project_improvement_agent, 
                 database_agent=None, backend_agent=None, frontend_agent=None,
                 devops_agent=None, project_management_agent=None,
                 response_optimizer_agent=None, request_analyzer_agent=None):
        
        # Inicializar agentes
        self.agents = {
            'code_analysis': code_analysis_agent,
            'project_improvement': project_improvement_agent,
            'database': database_agent,
            'backend': backend_agent,
            'frontend': frontend_agent,
            'devops': devops_agent,
            'project_management': project_management_agent
        }
        
        # Filtrar agentes não fornecidos
        self.agents = {k: v for k, v in self.agents.items() if v is not None}
        
        # Agentes especiais
        self.response_optimizer = response_optimizer_agent
        self.request_analyzer = request_analyzer_agent
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Gerenciador de arquivos centralizado
        self.file_manager = FileManager()
    
    def process_request(self, request_type: str, project_path: str, user_message: str) -> str:
        """Processa solicitações do usuário"""
        try:
            if not user_message:
                return "Por favor, forneça uma mensagem para processar."
            
            self.logger.info(f"Processando solicitação: {user_message[:50]}...")
            
            # Validar caminho do projeto
            self.validate_project_path(project_path)
            
            # Obter arquivos do projeto
            project_files = self.file_manager.get_files_with_content(project_path)
            if not project_files:
                return "Nenhum arquivo relevante encontrado no projeto."
            
            # Analisar a solicitação para determinar quais agentes são necessários
            required_agents = self._analyze_request(user_message)
            
            # Preparar contexto
            context = {
                'project_files': project_files,
                'user_message': user_message
            }
            
            # Processar com os agentes identificados
            responses = self._process_with_agents(
                required_agents, project_path, user_message, project_files, context
            )
            
            # Otimizar ou formatar respostas
            if self.response_optimizer and len(responses) > 1:
                combined_response = "\n\n".join([f"**{agent}**: {response}" 
                                               for agent, response in responses.items() 
                                               if 'error' not in response])
                
                return self.response_optimizer.optimize_response(combined_response, user_message)
            else:
                return self._format_raw_responses(responses)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar solicitação: {str(e)}")
            raise IntegrationError(f"Erro ao processar solicitação: {str(e)}")
    
    def _analyze_request(self, user_message: str) -> List[str]:
        """Analisa a solicitação para determinar quais agentes usar"""
        if self.request_analyzer:
            return self.request_analyzer.analyze_request(user_message)
        
        # Análise simplificada baseada em palavras-chave
        keywords = {
            'code_analysis': ['analisar código', 'qualidade', 'estrutura', 'padrões'],
            'project_improvement': ['melhorar', 'otimizar', 'refatorar'],
            'database': ['banco de dados', 'sql', 'modelo de dados'],
            'backend': ['backend', 'api', 'servidor'],
            'frontend': ['frontend', 'interface', 'ui', 'css', 'html'],
            'devops': ['devops', 'ci/cd', 'pipeline', 'deploy'],
            'project_management': ['gerenciamento', 'projeto', 'documentação']
        }
        
        required_agents = []
        message_lower = user_message.lower()
        
        for agent, terms in keywords.items():
            if agent in self.agents and any(term in message_lower for term in terms):
                required_agents.append(agent)
        
        # Se nenhum agente específico for identificado, use análise de código por padrão
        if not required_agents and 'code_analysis' in self.agents:
            required_agents.append('code_analysis')
        
        return required_agents
    
    # [Outros métodos existentes com otimizações]