# agents/code_analysis_agent.py
from agents.base_agent import BaseAgent

class CodeAnalysisAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model)
        
        # Extensões de arquivo para análise
        self.code_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.md': 'Markdown'
        }
    
    def analyze(self, project_path: str, user_request: str) -> str:
        """Analisa código com base na solicitação do usuário"""
        try:
            self.logger.info(f"Iniciando análise de código para {project_path}")
            self.logger.info(f"Solicitação do usuário: {user_request}")
            
            # Obter arquivos do projeto
            project_files = self.get_project_files(project_path, self.code_extensions)
            if not project_files:
                return "Nenhum arquivo de código encontrado para análise."
            
            # Criar visão geral do projeto
            overview = self.create_overview(project_files)
            
            # Ler conteúdo dos arquivos
            content = self.read_files(project_files)
            
            # Criar prompt de análise
            prompt = self._create_analysis_prompt(user_request, overview, content)
            
            self.logger.info("Gerando análise de código")
            return self.model.generate(prompt)
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar código: {str(e)}")
            raise Exception(f"Erro ao analisar código: {str(e)}")
    
    def _create_analysis_prompt(self, user_request: str, overview: str, content: str) -> str:
        """Cria um prompt detalhado para análise de código"""
        return f"""
        Analise o código a seguir com base na solicitação: {user_request}

        Visão Geral do Projeto:
        {overview}

        Conteúdo do Código:
        {content}

        Por favor, forneça:
        1. Análise da estrutura e organização do código
        2. Avaliação da qualidade do código
        3. Identificação de padrões e anti-padrões
        4. Sugestões de melhorias
        5. Exemplos de refatoração quando aplicável
        6. Análise de segurança e desempenho
        7. Recomendações de boas práticas

        Formate a resposta de forma clara e organizada, usando markdown.
        """