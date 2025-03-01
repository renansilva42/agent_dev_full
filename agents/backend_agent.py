# agents/backend_agent.py

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict

class BackendAgent:
    def __init__(self, model):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Backend-related file extensions
        self.backend_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cs': 'C#'
        }
        
        # Backend-related directories/files to look for
        self.backend_patterns = [
            'src/',
            'app/',
            'api/',
            'routes/',
            'controllers/',
            'services/',
            'middleware/',
            'utils/',
            'helpers/',
            'config/',
            'server/',
        ]
        
        # Backend-related file patterns
        self.backend_file_patterns = [
            'server',
            'app',
            'index',
            'main',
            'api',
            'route',
            'controller',
            'service',
            'middleware',
            'auth',
            'config'
        ]
    
    def analyze_backend(self, project_path: str, user_request: str) -> str:
        """
        Analyze backend-related aspects of the project
        """
        try:
            self.logger.info(f"Starting backend analysis for {project_path}")
            self.logger.info(f"User request: {user_request}")
            
            # Get backend-related files
            backend_files = self.get_backend_files(project_path)
            if not backend_files:
                return "Nenhum arquivo relacionado ao backend encontrado no projeto."
            
            # Create analysis overview
            overview = self.create_backend_overview(backend_files)
            
            # Read relevant files
            content = self.read_backend_files(backend_files)
            
            # Create analysis prompt
            prompt = f"""
            Analise os aspectos relacionados ao backend deste projeto com base na solicitação: {user_request}

            Visão Geral do Backend:
            {overview}

            Conteúdo dos Arquivos:
            {content}

            Por favor, forneça:
            1. Análise da arquitetura do backend
            2. Avaliação da estrutura de rotas e controllers
            3. Análise dos serviços e middlewares
            4. Identificação de padrões de projeto utilizados
            5. Avaliação da segurança e autenticação
            6. Análise de performance e escalabilidade
            7. Identificação de possíveis problemas
            8. Sugestões de melhorias e otimizações
            9. Recomendações de boas práticas
            10. Sugestões de modernização do código

            Formate a resposta de forma clara e organizada, usando markdown.
            """
            
            self.logger.info("Gerando análise do backend")
            return self.model.generate(prompt)
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar backend: {str(e)}")
            raise Exception(f"Erro ao analisar backend: {str(e)}")
    
    def get_backend_files(self, project_path: str) -> List[Dict]:
        """Get backend-related files from the project"""
        try:
            files = []
            path = Path(project_path)
            
            for item in path.rglob('*'):
                # Skip node_modules, venv, etc.
                if any(part.startswith('.') or part in {'node_modules', 'venv', 'env', '__pycache__'} 
                      for part in item.parts):
                    continue
                
                # Check if file is in a backend-related directory
                if any(pattern in str(item) for pattern in self.backend_patterns):
                    if item.is_file() and item.suffix in self.backend_extensions:
                        files.append({
                            'path': str(item),
                            'name': item.name,
                            'extension': item.suffix,
                            'language': self.backend_extensions[item.suffix],
                            'relative_path': str(item.relative_to(path))
                        })
                        continue
                
                # Check file name patterns
                if item.is_file() and item.suffix in self.backend_extensions:
                    stem = item.stem.lower()
                    if any(pattern in stem for pattern in self.backend_file_patterns):
                        files.append({
                            'path': str(item),
                            'name': item.name,
                            'extension': item.suffix,
                            'language': self.backend_extensions[item.suffix],
                            'relative_path': str(item.relative_to(path))
                        })
            
            self.logger.info(f"Found {len(files)} backend-related files")
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting backend files: {str(e)}")
            raise Exception(f"Error getting backend files: {str(e)}")
    
    def create_backend_overview(self, backend_files: List[Dict]) -> str:
        """Create an overview of backend-related files"""
        try:
            # Group files by language
            files_by_language = {}
            for file_info in backend_files:
                language = file_info['language']
                if language not in files_by_language:
                    files_by_language[language] = []
                files_by_language[language].append(file_info['relative_path'])
            
            # Create overview
            overview = ["Estrutura do Backend:", ""]
            
            for language, files in files_by_language.items():
                overview.append(f"Arquivos {language} ({len(files)}):")
                for file_path in sorted(files):
                    overview.append(f"  - {file_path}")
                overview.append("")
            
            return "\n".join(overview)
            
        except Exception as e:
            self.logger.error(f"Error creating backend overview: {str(e)}")
            return "Error creating backend overview"
    
    def read_backend_files(self, backend_files: List[Dict]) -> str:
        """Read and format backend-related files"""
        try:
            content = []
            
            for file_info in backend_files:
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        if file_content.strip():  # Only include non-empty files
                            content.append(
                                f"Arquivo: {file_info['relative_path']}\n"
                                f"Linguagem: {file_info['language']}\n\n"
                                f"```{file_info['language'].lower()}\n"
                                f"{file_content}\n"
                                f"```\n\n"
                            )
                except Exception as e:
                    self.logger.warning(f"Could not read file {file_info['path']}: {str(e)}")
            
            return "".join(content)
            
        except Exception as e:
            self.logger.error(f"Error reading backend files: {str(e)}")
            raise Exception(f"Error reading backend files: {str(e)}")
