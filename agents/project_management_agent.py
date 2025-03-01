# agents/project_management_agent.py

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict

class ProjectManagementAgent:
    def __init__(self, model):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Project management related files and directories
        self.pm_files = {
            # Documentation
            'README.md': 'Documentation',
            'CONTRIBUTING.md': 'Documentation',
            'CHANGELOG.md': 'Documentation',
            'LICENSE': 'Documentation',
            'docs/': 'Documentation',
            
            # Project configuration
            'package.json': 'Configuration',
            'setup.py': 'Configuration',
            'requirements.txt': 'Configuration',
            'pyproject.toml': 'Configuration',
            'poetry.lock': 'Configuration',
            'Pipfile': 'Configuration',
            
            # Project structure
            '.gitignore': 'Version Control',
            '.git/': 'Version Control',
            '.editorconfig': 'Code Style',
            
            # Testing
            'tests/': 'Testing',
            'test/': 'Testing',
            '__tests__/': 'Testing',
            'pytest.ini': 'Testing',
            'jest.config.js': 'Testing',
            
            # CI/CD configuration
            '.github/': 'CI/CD',
            '.gitlab-ci.yml': 'CI/CD',
            'jenkins/': 'CI/CD',
            
            # Dependencies
            'node_modules/': 'Dependencies',
            'venv/': 'Dependencies',
            'vendor/': 'Dependencies'
        }
        
        # Project management related patterns
        self.pm_patterns = [
            'docs/',
            'documentation/',
            'wiki/',
            'examples/',
            'samples/',
            'scripts/',
            'tools/',
            'utils/',
            'config/',
            'tests/',
            'test/',
            'coverage/'
        ]
    
    def analyze_project(self, project_path: str, user_request: str) -> str:
        """
        Analyze project management aspects
        """
        try:
            self.logger.info(f"Starting project management analysis for {project_path}")
            self.logger.info(f"User request: {user_request}")
            
            # Get project management related files
            pm_files = self.get_pm_files(project_path)
            if not pm_files:
                return "Nenhum arquivo relacionado ao gerenciamento do projeto encontrado."
            
            # Create analysis overview
            overview = self.create_pm_overview(pm_files)
            
            # Read relevant files
            content = self.read_pm_files(pm_files)
            
            # Create analysis prompt
            prompt = f"""
            Analise os aspectos relacionados ao gerenciamento do projeto com base na solicitação: {user_request}

            Visão Geral do Projeto:
            {overview}

            Conteúdo dos Arquivos:
            {content}

            Por favor, forneça:
            1. Análise da estrutura e organização do projeto
            2. Avaliação da documentação
            3. Análise do controle de versão
            4. Avaliação do processo de build e deployment
            5. Análise da gestão de dependências
            6. Avaliação dos testes e qualidade
            7. Análise do processo de desenvolvimento
            8. Identificação de boas práticas
            9. Identificação de possíveis problemas
            10. Sugestões de melhorias na organização
            11. Recomendações para documentação
            12. Sugestões para otimização do workflow

            Formate a resposta de forma clara e organizada, usando markdown.
            Destaque os pontos mais importantes e urgentes.
            """
            
            self.logger.info("Gerando análise do gerenciamento do projeto")
            return self.model.generate(prompt)
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar gerenciamento do projeto: {str(e)}")
            raise Exception(f"Erro ao analisar gerenciamento do projeto: {str(e)}")
    
    def get_pm_files(self, project_path: str) -> List[Dict]:
        """Get project management related files"""
        try:
            files = []
            path = Path(project_path)
            
            for item in path.rglob('*'):
                # Skip certain directories
                if any(part in ['node_modules', 'venv', '__pycache__'] for part in item.parts):
                    continue
                
                # Check if file/directory matches known patterns
                for pattern, file_type in self.pm_files.items():
                    if pattern.endswith('/'):
                        # Directory pattern
                        if pattern[:-1] in str(item):
                            if item.is_file():
                                files.append({
                                    'path': str(item),
                                    'name': item.name,
                                    'extension': item.suffix,
                                    'type': file_type,
                                    'relative_path': str(item.relative_to(path))
                                })
                    else:
                        # File pattern
                        if item.name == pattern or item.suffix == pattern:
                            if item.is_file():
                                files.append({
                                    'path': str(item),
                                    'name': item.name,
                                    'extension': item.suffix,
                                    'type': file_type,
                                    'relative_path': str(item.relative_to(path))
                                })
            
            self.logger.info(f"Found {len(files)} project management related files")
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting project management files: {str(e)}")
            raise Exception(f"Error getting project management files: {str(e)}")
    
    def create_pm_overview(self, pm_files: List[Dict]) -> str:
        """Create an overview of project management files"""
        try:
            # Group files by type
            files_by_type = {}
            for file_info in pm_files:
                file_type = file_info['type']
                if file_type not in files_by_type:
                    files_by_type[file_type] = []
                files_by_type[file_type].append(file_info['relative_path'])
            
            # Create overview
            overview = ["Estrutura do Projeto:", ""]
            
            # Order of sections
            section_order = [
                'Documentation',
                'Configuration',
                'Version Control',
                'Testing',
                'CI/CD',
                'Dependencies',
                'Code Style'
            ]
            
            # Add sections in order
            for section in section_order:
                if section in files_by_type:
                    files = files_by_type[section]
                    overview.append(f"Arquivos {section} ({len(files)}):")
                    for file_path in sorted(files):
                        overview.append(f"  - {file_path}")
                    overview.append("")
            
            # Add any remaining sections
            for file_type, files in files_by_type.items():
                if file_type not in section_order:
                    overview.append(f"Arquivos {file_type} ({len(files)}):")
                    for file_path in sorted(files):
                        overview.append(f"  - {file_path}")
                    overview.append("")
            
            return "\n".join(overview)
            
        except Exception as e:
            self.logger.error(f"Error creating project management overview: {str(e)}")
            return "Error creating project management overview"
    
    def read_pm_files(self, pm_files: List[Dict]) -> str:
        """Read and format project management files"""
        try:
            content = []
            
            # Priority files to read first
            priority_files = ['README.md', 'CONTRIBUTING.md', 'CHANGELOG.md']
            
            # Sort files to read priority files first
            sorted_files = sorted(
                pm_files,
                key=lambda x: (x['name'] not in priority_files, x['name'])
            )
            
            for file_info in sorted_files:
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        if file_content.strip():  # Only include non-empty files
                            # Determine language for code block
                            if file_info['extension'] in ['.md', '.txt']:
                                lang = 'markdown'
                            elif file_info['extension'] in ['.json', '.js']:
                                lang = 'javascript'
                            elif file_info['extension'] in ['.yml', '.yaml']:
                                lang = 'yaml'
                            elif file_info['extension'] == '.py':
                                lang = 'python'
                            else:
                                lang = 'plaintext'
                            
                            content.append(
                                f"Arquivo: {file_info['relative_path']}\n"
                                f"Tipo: {file_info['type']}\n\n"
                                f"```{lang}\n"
                                f"{file_content}\n"
                                f"```\n\n"
                            )
                except Exception as e:
                    self.logger.warning(f"Could not read file {file_info['path']}: {str(e)}")
            
            return "".join(content)
            
        except Exception as e:
            self.logger.error(f"Error reading project management files: {str(e)}")
            raise Exception(f"Error reading project management files: {str(e)}")
