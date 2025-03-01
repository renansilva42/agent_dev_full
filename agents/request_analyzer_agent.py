# agents/request_analyzer_agent.py

import logging
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import deque

@dataclass
class ConversationContext:
    """Store context about the current conversation"""
    last_topic: str = None
    last_files_discussed: List[str] = None
    last_code_suggestions: Dict[str, str] = None
    conversation_history: deque = None
    
    def __init__(self):
        self.conversation_history = deque(maxlen=5)  # Keep last 5 messages
    
    def add_message(self, message: str, response: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            'message': message,
            'response': response
        })
    
    def get_last_context(self) -> Dict:
        """Get context from last conversation"""
        if not self.conversation_history:
            return {}
        return self.conversation_history[-1]

class RequestAnalyzerAgent:
    def __init__(self, model):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.context = ConversationContext()
        
        # Request type patterns and their corresponding agents
        self.request_patterns = {
            'frontend': {
                'patterns': {
                    'interface', 'ui', 'ux', 'design', 'componente', 'layout',
                    'estilo', 'css', 'html', 'javascript', 'responsivo', 'tela',
                    'visual', 'frontend', 'front-end', 'front end', 'página',
                    'site', 'web', 'botão', 'formulário', 'menu', 'navegação'
                },
                'agents': ['frontend']
            },
            'backend': {
                'patterns': {
                    'api', 'servidor', 'endpoint', 'rota', 'controller',
                    'serviço', 'middleware', 'autenticação', 'backend',
                    'back-end', 'back end', 'processamento', 'requisição'
                },
                'agents': ['backend']
            },
            'database': {
                'patterns': {
                    'banco de dados', 'database', 'db', 'dados', 'tabela',
                    'sql', 'modelo de dados', 'schema', 'banco', 'modelagem'
                },
                'agents': ['database']
            },
            'devops': {
                'patterns': {
                    'deploy', 'ci/cd', 'pipeline', 'infraestrutura', 'docker',
                    'kubernetes', 'container', 'ambiente', 'monitoramento',
                    'log', 'devops', 'dev ops'
                },
                'agents': ['devops']
            },
            'project_structure': {
                'patterns': {
                    'estrutura', 'organização', 'arquitetura', 'projeto',
                    'pastas', 'arquivos', 'dependências', 'módulos'
                },
                'agents': ['project_management']
            },
            'code_quality': {
                'patterns': {
                    'qualidade', 'melhoria', 'otimização', 'performance',
                    'segurança', 'bug', 'erro', 'problema', 'refatoração'
                },
                'agents': ['code_analysis', 'project_improvement']
            }
        }
        
        # Reference patterns for code requests
        self.code_request_patterns = {
            'implementation': {
                'me dê o código', 'implemente', 'código completo',
                'implementação', 'como implementar', 'mostre o código',
                'exemplo de código', 'código para', 'código pronto'
            },
            'modification': {
                'atualize', 'modifique', 'altere', 'mude', 'corrija',
                'ajuste', 'adapte', 'refatore', 'melhore'
            },
            'previous_context': {
                'sugeriu', 'mencionou', 'falou', 'citou', 'anterior',
                'última', 'último', 'anterior', 'acima', 'sugestões'
            }
        }
    
    def analyze_request(self, user_request: str) -> Dict:
        """
        Analyze user request and determine which agents should handle it
        
        Returns:
            Dict containing:
            - agents_to_use: List of agent names to handle the request
            - analysis_type: Type of analysis needed
            - context: Additional context for the agents
        """
        try:
            self.logger.info(f"Analyzing request: {user_request}")
            
            # Check if request refers to previous context
            refers_to_previous = self._check_previous_context_reference(user_request)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(user_request, refers_to_previous)
            
            # Get AI analysis
            analysis = self.model.generate(prompt)
            
            # Determine required agents based on the analysis
            required_agents = self._determine_required_agents(user_request, analysis, refers_to_previous)
            
            # Determine if code examples are needed
            needs_code = self._needs_code_examples(user_request, analysis)
            
            # Create context for the agents
            context = {
                'original_request': user_request,
                'needs_code_examples': needs_code,
                'analysis': analysis,
                'refers_to_previous': refers_to_previous,
                'previous_context': self.context.get_last_context() if refers_to_previous else None,
                'last_topic': self.context.last_topic,
                'last_files_discussed': self.context.last_files_discussed,
                'last_code_suggestions': self.context.last_code_suggestions
            }
            
            # Update conversation context
            self.context.last_topic = self._determine_topic(required_agents)
            
            result = {
                'agents_to_use': required_agents,
                'analysis_type': self._determine_analysis_type(required_agents),
                'context': context
            }
            
            self.logger.info(f"Analysis result: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing request: {str(e)}")
            raise Exception(f"Erro ao analisar solicitação: {str(e)}")
    
    def update_context(self, user_message: str, response: str, files_discussed: List[str] = None,
                      code_suggestions: Dict[str, str] = None):
        """Update conversation context with new information"""
        self.context.add_message(user_message, response)
        if files_discussed:
            self.context.last_files_discussed = files_discussed
        if code_suggestions:
            self.context.last_code_suggestions = code_suggestions
    
    def _create_analysis_prompt(self, request: str, refers_to_previous: bool) -> str:
        """Create a context-aware analysis prompt"""
        prompt = f"""
        Analise a seguinte solicitação do usuário e determine a melhor forma de respondê-la:

        Solicitação: {request}
        """
        
        if refers_to_previous:
            last_context = self.context.get_last_context()
            if last_context:
                prompt += f"""
                
                Contexto da Conversa Anterior:
                Última Solicitação: {last_context.get('message', '')}
                Última Resposta: {last_context.get('response', '')}
                Último Tópico: {self.context.last_topic or 'Nenhum'}
                """
        
        prompt += """
        Por favor, identifique:
        1. Qual é o objetivo principal da solicitação?
        2. A solicitação se refere a uma conversa anterior?
        3. Quais aspectos específicos do sistema precisam ser analisados?
        4. A solicitação requer código pronto para implementação?
        5. Quais arquivos ou componentes específicos são relevantes?
        
        Forneça sua análise em um formato estruturado que eu possa processar.
        """
        
        return prompt
    
    def _check_previous_context_reference(self, request: str) -> bool:
        """Check if request refers to previous conversation"""
        request_lower = request.lower()
        return any(
            pattern in request_lower
            for patterns in self.code_request_patterns.values()
            for pattern in patterns
        )
    
    def _determine_required_agents(self, request: str, analysis: str, refers_to_previous: bool) -> List[str]:
        """Determine which agents should handle the request"""
        if refers_to_previous and self.context.last_topic:
            # Use the same agents as the previous request
            return self._get_agents_for_topic(self.context.last_topic)
        
        request_lower = request.lower()
        required_agents = set()
        
        # Check patterns for each type of request
        for req_type, config in self.request_patterns.items():
            if any(pattern in request_lower for pattern in config['patterns']):
                required_agents.update(config['agents'])
        
        # If no specific agents were identified, use code analysis as default
        if not required_agents:
            required_agents.add('code_analysis')
        
        return list(required_agents)
    
    def _get_agents_for_topic(self, topic: str) -> List[str]:
        """Get relevant agents for a topic"""
        return self.request_patterns.get(topic, {}).get('agents', ['code_analysis'])
    
    def _determine_topic(self, agents: List[str]) -> str:
        """Determine the main topic based on required agents"""
        if 'frontend' in agents:
            return 'frontend'
        elif 'backend' in agents:
            return 'backend'
        elif 'database' in agents:
            return 'database'
        elif 'devops' in agents:
            return 'devops'
        return 'code_quality'
    
    def _determine_analysis_type(self, agents: List[str]) -> str:
        """Determine the type of analysis needed based on required agents"""
        if len(agents) == len(self.request_patterns):
            return 'full_analysis'
        elif len(agents) == 1:
            return f'{agents[0]}_analysis'
        else:
            return 'partial_analysis'
    
    def _needs_code_examples(self, request: str, analysis: str) -> bool:
        """Determine if the response should include code examples"""
        request_lower = request.lower()
        
        # Check for direct code requests
        for patterns in self.code_request_patterns.values():
            if any(pattern in request_lower for pattern in patterns):
                return True
        
        # Check for implementation-related terms
        code_related_terms = {
            'código', 'implementação', 'exemplo', 'como fazer',
            'mostre', 'demonstre', 'implemente', 'crie', 'modifique',
            'atualize', 'corrija', 'otimize', 'melhore'
        }
        
        return any(term in request_lower for term in code_related_terms)
