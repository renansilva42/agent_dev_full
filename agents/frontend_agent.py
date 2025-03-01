# agents/frontend_agent.py

import logging
from pathlib import Path
from typing import Dict, List, Optional

class FrontendAgent:
    def __init__(self, model):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Frontend file patterns
        self.frontend_patterns = {
            'html': ['.html', '.htm', '.xhtml'],
            'css': ['.css', '.scss', '.sass', '.less'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
            'assets': ['.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico'],
            'config': ['package.json', 'webpack.config.js', 'babel.config.js', 'tsconfig.json']
        }
        
        # Max files to analyze per type
        self.max_files_per_type = 5
    
    def analyze_frontend(self, project_path: str, user_message: str) -> str:
        """Analyze frontend code and suggest improvements"""
        try:
            self.logger.info(f"Starting frontend analysis for {project_path}")
            self.logger.info(f"User request: {user_message}")
            
            # Get relevant frontend files
            frontend_files = self._get_frontend_files(project_path)
            if not frontend_files:
                return "Nenhum arquivo frontend encontrado no projeto."
            
            # Read file contents
            file_contents = self._read_relevant_files(frontend_files, user_message)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(user_message, file_contents)
            
            # Generate analysis
            self.logger.info("Gerando análise do frontend")
            return self.model.generate(prompt, file_contents)
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar frontend: {str(e)}")
            raise Exception(f"Erro ao analisar frontend: {str(e)}")
    
    def _get_frontend_files(self, project_path: str) -> Dict[str, List[Path]]:
        """Get frontend-related files from the project"""
        try:
            files: Dict[str, List[Path]] = {
                'html': [],
                'css': [],
                'javascript': [],
                'assets': [],
                'config': []
            }
            
            path = Path(project_path)
            
            # Directories to ignore
            ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.env'}
            
            for item in path.rglob('*'):
                # Skip ignored directories
                if any(ignore_dir in item.parts for ignore_dir in ignore_dirs):
                    continue
                
                # Categorize files by type
                if item.is_file():
                    for file_type, extensions in self.frontend_patterns.items():
                        if any(str(item).lower().endswith(ext) for ext in extensions):
                            files[file_type].append(item)
                            break
            
            # Log found files
            total_files = sum(len(files_list) for files_list in files.values())
            self.logger.info(f"Found {total_files} frontend-related files")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting frontend files: {str(e)}")
            return {}
    
    def _read_relevant_files(self, files: Dict[str, List[Path]], user_message: str) -> Dict[str, str]:
        """Read and filter relevant files based on user request"""
        try:
            contents = {}
            message_lower = user_message.lower()
            
            # Keywords to look for in filenames based on user message
            keywords = set(message_lower.split())
            
            for file_type, file_list in files.items():
                # Sort files by relevance
                sorted_files = self._sort_files_by_relevance(file_list, keywords)
                
                # Take only the most relevant files up to the limit
                for file_path in sorted_files[:self.max_files_per_type]:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            relative_path = str(file_path.relative_to(Path.cwd()))
                            contents[relative_path] = f.read()
                    except Exception as e:
                        self.logger.warning(f"Could not read file {file_path}: {str(e)}")
            
            return contents
            
        except Exception as e:
            self.logger.error(f"Error reading files: {str(e)}")
            return {}
    
    def _sort_files_by_relevance(self, files: List[Path], keywords: set) -> List[Path]:
        """Sort files by relevance to user request"""
        def calculate_relevance(file_path: Path) -> int:
            score = 0
            path_str = str(file_path).lower()
            
            # Check for keywords in path
            for keyword in keywords:
                if keyword in path_str:
                    score += 1
            
            # Prioritize main/index files
            if 'main' in path_str or 'index' in path_str:
                score += 2
            
            # Prioritize non-generated files
            if 'dist' in path_str or 'build' in path_str:
                score -= 1
            
            return score
        
        return sorted(files, key=calculate_relevance, reverse=True)
    
    def _create_analysis_prompt(self, user_message: str, file_contents: Dict[str, str]) -> str:
        """Create a prompt for frontend analysis"""
        prompt = f"""
        Analise o frontend do projeto com base na seguinte solicitação:
        {user_message}

        Por favor, forneça:
        1. Análise detalhada dos arquivos frontend
        2. Sugestões específicas de melhorias
        3. Exemplos de código para implementação
        4. Instruções claras de onde aplicar cada mudança

        Regras importantes:
        1. SEMPRE use o formato:
           [caminho/do/arquivo.ext]
           ```linguagem
           código completo
           ```
        
        2. Para alterações, use o formato:
           [caminho/do/arquivo.ext]
           ```linguagem
           // ANTES
           código original
           
           // DEPOIS
           código modificado com alterações
           ```
        
        3. Para novos arquivos:
           - Especifique o caminho completo onde criar
           - Forneça o código completo e funcional
           - Indique dependências necessárias
        
        4. Para modificações:
           - Mostre o contexto completo
           - Use + para linhas adicionadas
           - Use - para linhas removidas
           - Mantenha a estrutura do projeto

        Arquivos do Projeto:
        """
        
        # Add file contents to prompt
        for file_path, content in file_contents.items():
            prompt += f"\n[{file_path}]\n```\n{content}\n```\n"
        
        return prompt
