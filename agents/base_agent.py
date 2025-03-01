# agents/base_agent.py
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Set
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Classe base para todos os agentes de análise"""
    
    def __init__(self, model, logger=None):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        
        # Diretórios a serem ignorados
        self.ignore_dirs: Set[str] = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.env'}
    
    @abstractmethod
    def analyze(self, project_path: str, user_request: str) -> str:
        """Método principal de análise a ser implementado por subclasses"""
        pass
    
    def get_project_files(self, project_path: str, extensions: Dict[str, str] = None) -> List[Dict]:
        """Método comum para obter arquivos do projeto"""
        try:
            files = []
            path = Path(project_path)
            
            for item in path.rglob('*'):
                # Ignorar diretórios específicos
                if any(ignore_dir in item.parts for ignore_dir in self.ignore_dirs):
                    continue
                
                # Incluir apenas arquivos com extensões relevantes se especificado
                if extensions and item.is_file() and item.suffix in extensions:
                    files.append({
                        'path': str(item),
                        'name': item.name,
                        'extension': item.suffix,
                        'language': extensions.get(item.suffix, 'Unknown'),
                        'relative_path': str(item.relative_to(path))
                    })
                elif not extensions and item.is_file():
                    files.append({
                        'path': str(item),
                        'name': item.name,
                        'extension': item.suffix,
                        'language': 'Unknown',
                        'relative_path': str(item.relative_to(path))
                    })
            
            self.logger.info(f"Encontrados {len(files)} arquivos para análise")
            return files
            
        except Exception as e:
            self.logger.error(f"Erro ao obter arquivos do projeto: {str(e)}")
            raise Exception(f"Erro ao obter arquivos do projeto: {str(e)}")
    
    def create_overview(self, files: List[Dict], group_by: str = 'language') -> str:
        """Cria uma visão geral dos arquivos do projeto"""
        try:
            # Agrupar arquivos pelo critério especificado
            files_by_group = {}
            for file_info in files:
                group = file_info.get(group_by, 'Unknown')
                if group not in files_by_group:
                    files_by_group[group] = []
                files_by_group[group].append(file_info['relative_path'])
            
            # Criar visão geral
            overview = ["Estrutura do Projeto:", ""]
            
            for group, files in files_by_group.items():
                overview.append(f"Arquivos {group} ({len(files)}):")
                for file_path in sorted(files):
                    overview.append(f"  - {file_path}")
                overview.append("")
            
            return "\n".join(overview)
            
        except Exception as e:
            self.logger.error(f"Erro ao criar visão geral: {str(e)}")
            return "Erro ao criar visão geral do projeto"
    
    def read_files(self, files: List[Dict]) -> str:
        """Lê e formata o conteúdo dos arquivos"""
        try:
            content = []
            
            for file_info in files:
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        if file_content.strip():  # Incluir apenas arquivos não vazios
                            language = file_info.get('language', 'plaintext').lower()
                            content.append(
                                f"Arquivo: {file_info['relative_path']}\n"
                                f"Linguagem: {file_info.get('language', 'Unknown')}\n\n"
                                f"```{language}\n"
                                f"{file_content}\n"
                                f"```\n\n"
                            )
                except Exception as e:
                    self.logger.warning(f"Não foi possível ler o arquivo {file_info['path']}: {str(e)}")
            
            return "".join(content)
            
        except Exception as e:
            self.logger.error(f"Erro ao ler arquivos: {str(e)}")
            raise Exception(f"Erro ao ler arquivos: {str(e)}")