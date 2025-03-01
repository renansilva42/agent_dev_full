# agents/database_agent.py

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict

class DatabaseAgent:
    def __init__(self, model):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Database-related file extensions
        self.db_extensions = {
            '.sql': 'SQL',
            '.prisma': 'Prisma',
            '.orm': 'ORM',
            '.migration': 'Migration',
            '.db': 'Database'
        }
        
        # Database-related directories/files to look for
        self.db_patterns = [
            'migrations/',
            'database/',
            'db/',
            'models/',
            'schemas/',
            'prisma/',
            'sequelize/',
            'typeorm/',
            'mongoose/',
            'knex/',
        ]
    
    def analyze_database(self, project_path: str, user_request: str) -> str:
        """
        Analyze database-related aspects of the project
        """
        try:
            self.logger.info(f"Starting database analysis for {project_path}")
            self.logger.info(f"User request: {user_request}")
            
            # Get database-related files
            db_files = self.get_database_files(project_path)
            if not db_files:
                return "Nenhum arquivo relacionado a banco de dados encontrado no projeto."
            
            # Create analysis overview
            overview = self.create_db_overview(db_files)
            
            # Read relevant files
            content = self.read_db_files(db_files)
            
            # Create analysis prompt
            prompt = f"""
            Analise os aspectos relacionados a banco de dados deste projeto com base na solicitação: {user_request}

            Visão Geral do Banco de Dados:
            {overview}

            Conteúdo dos Arquivos:
            {content}

            Por favor, forneça:
            1. Análise da estrutura do banco de dados
            2. Avaliação dos modelos e schemas
            3. Análise das migrações (se houver)
            4. Identificação de possíveis problemas
            5. Sugestões de otimização
            6. Boas práticas de banco de dados
            7. Recomendações de segurança
            8. Sugestões de melhorias na modelagem

            Formate a resposta de forma clara e organizada, usando markdown.
            """
            
            self.logger.info("Gerando análise de banco de dados")
            return self.model.generate(prompt)
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar banco de dados: {str(e)}")
            raise Exception(f"Erro ao analisar banco de dados: {str(e)}")
    
    def get_database_files(self, project_path: str) -> List[Dict]:
        """Get database-related files from the project"""
        try:
            files = []
            path = Path(project_path)
            
            for item in path.rglob('*'):
                # Check if file is in a database-related directory
                if any(pattern in str(item) for pattern in self.db_patterns):
                    if item.is_file():
                        files.append({
                            'path': str(item),
                            'name': item.name,
                            'extension': item.suffix,
                            'type': self.db_extensions.get(item.suffix, 'Other'),
                            'relative_path': str(item.relative_to(path))
                        })
                        continue
                
                # Check file extensions
                if item.is_file() and item.suffix in self.db_extensions:
                    files.append({
                        'path': str(item),
                        'name': item.name,
                        'extension': item.suffix,
                        'type': self.db_extensions[item.suffix],
                        'relative_path': str(item.relative_to(path))
                    })
            
            self.logger.info(f"Found {len(files)} database-related files")
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting database files: {str(e)}")
            raise Exception(f"Error getting database files: {str(e)}")
    
    def create_db_overview(self, db_files: List[Dict]) -> str:
        """Create an overview of database-related files"""
        try:
            # Group files by type
            files_by_type = {}
            for file_info in db_files:
                file_type = file_info['type']
                if file_type not in files_by_type:
                    files_by_type[file_type] = []
                files_by_type[file_type].append(file_info['relative_path'])
            
            # Create overview
            overview = ["Estrutura do Banco de Dados:", ""]
            
            for file_type, files in files_by_type.items():
                overview.append(f"Arquivos {file_type} ({len(files)}):")
                for file_path in sorted(files):
                    overview.append(f"  - {file_path}")
                overview.append("")
            
            return "\n".join(overview)
            
        except Exception as e:
            self.logger.error(f"Error creating database overview: {str(e)}")
            return "Error creating database overview"
    
    def read_db_files(self, db_files: List[Dict]) -> str:
        """Read and format database-related files"""
        try:
            content = []
            
            for file_info in db_files:
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        if file_content.strip():  # Only include non-empty files
                            content.append(
                                f"Arquivo: {file_info['relative_path']}\n"
                                f"Tipo: {file_info['type']}\n\n"
                                f"```{file_info['type'].lower()}\n"
                                f"{file_content}\n"
                                f"```\n\n"
                            )
                except Exception as e:
                    self.logger.warning(f"Could not read file {file_info['path']}: {str(e)}")
            
            return "".join(content)
            
        except Exception as e:
            self.logger.error(f"Error reading database files: {str(e)}")
            raise Exception(f"Error reading database files: {str(e)}")
