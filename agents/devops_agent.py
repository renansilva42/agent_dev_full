# agents/devops_agent.py

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict

class DevOpsAgent:
    def __init__(self, model):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # DevOps-related file extensions and types
        self.devops_files = {
            # Docker
            'Dockerfile': 'Docker',
            'docker-compose.yml': 'Docker',
            'docker-compose.yaml': 'Docker',
            '.dockerignore': 'Docker',
            
            # CI/CD
            '.gitlab-ci.yml': 'GitLab CI',
            '.travis.yml': 'Travis CI',
            'azure-pipelines.yml': 'Azure Pipelines',
            'Jenkinsfile': 'Jenkins',
            '.github/workflows': 'GitHub Actions',
            'bitbucket-pipelines.yml': 'Bitbucket Pipelines',
            
            # Infrastructure as Code
            'terraform.tf': 'Terraform',
            '.tf': 'Terraform',
            'main.tf': 'Terraform',
            'cloudformation.yml': 'CloudFormation',
            'serverless.yml': 'Serverless',
            
            # Configuration
            '.env.example': 'Environment',
            '.env.template': 'Environment',
            'nginx.conf': 'Nginx',
            'apache.conf': 'Apache',
            
            # Kubernetes
            'kubernetes/': 'Kubernetes',
            'k8s/': 'Kubernetes',
            '.yaml': 'Kubernetes',
            '.yml': 'Kubernetes',
            
            # Scripts
            '.sh': 'Shell Script',
            '.bash': 'Shell Script',
            '.ps1': 'PowerShell'
        }
        
        # DevOps-related directories to look for
        self.devops_patterns = [
            '.github/',
            '.gitlab/',
            'ci/',
            'cd/',
            'pipeline/',
            'deploy/',
            'kubernetes/',
            'k8s/',
            'docker/',
            'terraform/',
            'ansible/',
            'scripts/',
            'config/',
            'infrastructure/'
        ]
    
    def analyze_devops(self, project_path: str, user_request: str) -> str:
        """
        Analyze DevOps-related aspects of the project
        """
        try:
            self.logger.info(f"Starting DevOps analysis for {project_path}")
            self.logger.info(f"User request: {user_request}")
            
            # Get DevOps-related files
            devops_files = self.get_devops_files(project_path)
            if not devops_files:
                return "Nenhum arquivo relacionado a DevOps encontrado no projeto."
            
            # Create analysis overview
            overview = self.create_devops_overview(devops_files)
            
            # Read relevant files
            content = self.read_devops_files(devops_files)
            
            # Create analysis prompt
            prompt = f"""
            Analise os aspectos relacionados a DevOps deste projeto com base na solicitação: {user_request}

            Visão Geral de DevOps:
            {overview}

            Conteúdo dos Arquivos:
            {content}

            Por favor, forneça:
            1. Análise da infraestrutura e configuração
            2. Avaliação dos pipelines de CI/CD
            3. Análise da containerização (Docker, Kubernetes, etc.)
            4. Avaliação das práticas de deployment
            5. Análise de segurança e compliance
            6. Avaliação de monitoramento e logging
            7. Análise de escalabilidade
            8. Identificação de possíveis problemas
            9. Sugestões de melhorias e otimizações
            10. Recomendações de boas práticas
            11. Sugestões de modernização da infraestrutura
            12. Análise de custos e eficiência

            Formate a resposta de forma clara e organizada, usando markdown.
            """
            
            self.logger.info("Gerando análise de DevOps")
            return self.model.generate(prompt)
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar DevOps: {str(e)}")
            raise Exception(f"Erro ao analisar DevOps: {str(e)}")
    
    def get_devops_files(self, project_path: str) -> List[Dict]:
        """Get DevOps-related files from the project"""
        try:
            files = []
            path = Path(project_path)
            
            for item in path.rglob('*'):
                # Skip hidden directories and node_modules
                if any(part.startswith('.') or part == 'node_modules' for part in item.parts):
                    if not any(devops_dir in str(item) for devops_dir in ['.github', '.gitlab']):
                        continue
                
                # Check if file is in a DevOps-related directory
                if any(pattern in str(item) for pattern in self.devops_patterns):
                    if item.is_file():
                        files.append({
                            'path': str(item),
                            'name': item.name,
                            'extension': item.suffix,
                            'type': self.get_file_type(item),
                            'relative_path': str(item.relative_to(path))
                        })
                        continue
                
                # Check for specific DevOps files
                if item.is_file():
                    file_type = self.get_file_type(item)
                    if file_type:
                        files.append({
                            'path': str(item),
                            'name': item.name,
                            'extension': item.suffix,
                            'type': file_type,
                            'relative_path': str(item.relative_to(path))
                        })
            
            self.logger.info(f"Found {len(files)} DevOps-related files")
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting DevOps files: {str(e)}")
            raise Exception(f"Error getting DevOps files: {str(e)}")
    
    def get_file_type(self, file_path: Path) -> Optional[str]:
        """Determine the type of a DevOps-related file"""
        # Check exact file names first
        if file_path.name in self.devops_files:
            return self.devops_files[file_path.name]
        
        # Check file extensions
        if file_path.suffix in self.devops_files:
            return self.devops_files[file_path.suffix]
        
        # Check if file is in a specific directory
        for pattern, file_type in self.devops_files.items():
            if pattern.endswith('/') and pattern in str(file_path):
                return file_type
        
        return None
    
    def create_devops_overview(self, devops_files: List[Dict]) -> str:
        """Create an overview of DevOps-related files"""
        try:
            # Group files by type
            files_by_type = {}
            for file_info in devops_files:
                file_type = file_info['type']
                if file_type not in files_by_type:
                    files_by_type[file_type] = []
                files_by_type[file_type].append(file_info['relative_path'])
            
            # Create overview
            overview = ["Estrutura DevOps:", ""]
            
            for file_type, files in files_by_type.items():
                overview.append(f"Arquivos {file_type} ({len(files)}):")
                for file_path in sorted(files):
                    overview.append(f"  - {file_path}")
                overview.append("")
            
            return "\n".join(overview)
            
        except Exception as e:
            self.logger.error(f"Error creating DevOps overview: {str(e)}")
            return "Error creating DevOps overview"
    
    def read_devops_files(self, devops_files: List[Dict]) -> str:
        """Read and format DevOps-related files"""
        try:
            content = []
            
            for file_info in devops_files:
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        if file_content.strip():  # Only include non-empty files
                            content.append(
                                f"Arquivo: {file_info['relative_path']}\n"
                                f"Tipo: {file_info['type']}\n\n"
                                f"```yaml\n"  # Most DevOps files are YAML or similar
                                f"{file_content}\n"
                                f"```\n\n"
                            )
                except Exception as e:
                    self.logger.warning(f"Could not read file {file_info['path']}: {str(e)}")
            
            return "".join(content)
            
        except Exception as e:
            self.logger.error(f"Error reading DevOps files: {str(e)}")
            raise Exception(f"Error reading DevOps files: {str(e)}")
