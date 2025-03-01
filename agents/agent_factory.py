# agents/agent_factory.py
import logging
from typing import Dict, Any, Optional

class AgentFactory:
    """Factory para criação de agentes"""
    
    def __init__(self, model):
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    def create_agent(self, agent_type: str) -> Any:
        """Cria e retorna uma instância do agente especificado"""
        try:
            if agent_type == 'code_analysis':
                from agents.code_analysis_agent import CodeAnalysisAgent
                return CodeAnalysisAgent(self.model)
                
            elif agent_type == 'project_improvement':
                from agents.project_improvement_agent import ProjectImprovementAgent
                return ProjectImprovementAgent(self.model)
                
            elif agent_type == 'database':
                from agents.database_agent import DatabaseAgent
                return DatabaseAgent(self.model)
                
            elif agent_type == 'backend':
                from agents.backend_agent import BackendAgent
                return BackendAgent(self.model)
                
            elif agent_type == 'frontend':
                from agents.frontend_agent import FrontendAgent
                return FrontendAgent(self.model)
                
            elif agent_type == 'devops':
                from agents.devops_agent import DevOpsAgent
                return DevOpsAgent(self.model)
                
            elif agent_type == 'project_management':
                from agents.project_management_agent import ProjectManagementAgent
                return ProjectManagementAgent(self.model)
                
            elif agent_type == 'response_optimizer':
                from agents.response_optimizer_agent import ResponseOptimizerAgent
                return ResponseOptimizerAgent(self.model)
                
            elif agent_type == 'request_analyzer':
                from agents.request_analyzer_agent import RequestAnalyzerAgent
                return RequestAnalyzerAgent(self.model)
                
            else:
                self.logger.error(f"Tipo de agente desconhecido: {agent_type}")
                raise ValueError(f"Tipo de agente desconhecido: {agent_type}")
                
        except Exception as e:
            self.logger.error(f"Erro ao criar agente {agent_type}: {str(e)}")
            raise Exception(f"Erro ao criar agente {agent_type}: {str(e)}")