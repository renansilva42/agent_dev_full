# agents/project_improvement_agent.py

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict

class ProjectImprovementAgent:
    def __init__(self, model):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # File extensions to analyze
        self.code_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.md': 'Markdown'
        }
        
        # Directories to ignore
        self.ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.env'}
    
    def suggest_improvements(self, project_path: str, user_request: str) -> str:
        """
        Analyze project and suggest improvements based on user's specific request
        """
        try:
            self.logger.info(f"Iniciando análise de melhorias para {project_path}")
            self.logger.info(f"Solicitação do usuário: {user_request}")
            
            if not os.path.exists(project_path):
                raise ValueError(f"Caminho do projeto não existe: {project_path}")
            
            # Get project files
            project_files = self.get_project_files(project_path)
            if not project_files:
                raise ValueError("Nenhum arquivo de código encontrado para análise")
            
            # Create project overview
            overview = self.create_project_overview(project_files)
            
            # Read relevant files
            code_content = self.read_project_files(project_files)
            
            # Create improvement prompt based on user request
            prompt = f"""
            Analise o código a seguir e sugira melhorias com base nesta solicitação: {user_request}

            Visão Geral do Projeto:
            {overview}

            Conteúdo do Código:
            {code_content}

            Por favor, forneça:
            1. Melhorias específicas para cada arquivo relevante
            2. Exemplos de código mostrando as mudanças sugeridas
            3. Explicações claras de por que cada mudança é recomendada
            4. Localização exata onde as mudanças devem ser feitas
            5. Possíveis impactos ou considerações sobre as mudanças
            6. Alternativas modernas ou melhores práticas a considerar
            7. Guia passo a passo de implementação quando aplicável

            Formate a resposta com:
            - Seções claras com títulos
            - Marcadores para listar itens
            - Blocos de código usando ``` mostrando exemplos antes/depois
            - Destaque para nomes de arquivos
            - Explicações claras e objetivas
            - Priorização das melhorias mais importantes

            Use Português do Brasil e mantenha um tom profissional mas amigável.
            """
            
            self.logger.info("Gerando sugestões de melhorias")
            return self.model.generate(prompt)
            
        except Exception as e:
            self.logger.error(f"Erro ao sugerir melhorias: {str(e)}")
            raise Exception(f"Erro ao sugerir melhorias: {str(e)}")
    
    def get_project_files(self, project_path: str) -> List[Dict]:
        """Get list of relevant files in the project"""
        try:
            files = []
            path = Path(project_path)
            
            for item in path.rglob('*'):
                # Skip ignored directories
                if any(ignore_dir in item.parts for ignore_dir in self.ignore_dirs):
                    continue
                
                # Include only files with relevant extensions
                if item.is_file() and item.suffix in self.code_extensions:
                    files.append({
                        'path': str(item),
                        'name': item.name,
                        'extension': item.suffix,
                        'language': self.code_extensions[item.suffix],
                        'relative_path': str(item.relative_to(path))
                    })
            
            self.logger.info(f"Encontrados {len(files)} arquivos para análise")
            return files
            
        except Exception as e:
            self.logger.error(f"Erro ao obter arquivos do projeto: {str(e)}")
            raise Exception(f"Erro ao obter arquivos do projeto: {str(e)}")
    
    def create_project_overview(self, project_files: List[Dict]) -> str:
        """Create an overview of the project structure"""
        try:
            # Group files by language
            files_by_language = {}
            for file_info in project_files:
                language = file_info['language']
                if language not in files_by_language:
                    files_by_language[language] = []
                files_by_language[language].append(file_info['relative_path'])
            
            # Create overview
            overview = ["Estrutura do Projeto:", ""]
            
            for language, files in files_by_language.items():
                overview.append(f"Arquivos {language} ({len(files)}):")
                for file_path in sorted(files):
                    overview.append(f"  - {file_path}")
                overview.append("")
            
            return "\n".join(overview)
            
        except Exception as e:
            self.logger.error(f"Erro ao criar visão geral do projeto: {str(e)}")
            return "Erro ao criar visão geral do projeto"
    
    def read_project_files(self, project_files: List[Dict]) -> str:
        """Read and format the content of project files"""
        try:
            code_content = []
            
            for file_info in project_files:
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():  # Only include non-empty files
                            code_content.append(
                                f"Arquivo: {file_info['relative_path']}\n"
                                f"Linguagem: {file_info['language']}\n\n"
                                f"```{file_info['language'].lower()}\n"
                                f"{content}\n"
                                f"```\n\n"
                            )
                except Exception as e:
                    self.logger.warning(f"Não foi possível ler o arquivo {file_info['path']}: {str(e)}")
            
            return "".join(code_content)
            
        except Exception as e:
            self.logger.error(f"Erro ao ler arquivos do projeto: {str(e)}")
            raise Exception(f"Erro ao ler arquivos do projeto: {str(e)}")
