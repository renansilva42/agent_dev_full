# integration/integration_layer.py

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

class IntegrationError(Exception):
    """Custom exception for integration layer errors"""
    pass

class IntegrationLayer:
    def __init__(self, code_analysis_agent, project_improvement_agent, database_agent=None,
                 backend_agent=None, frontend_agent=None, devops_agent=None, 
                 project_management_agent=None, response_optimizer_agent=None,
                 request_analyzer_agent=None):
        """Initialize with all available agents"""
        self.agents = {
            'code_analysis': code_analysis_agent,
            'project_improvement': project_improvement_agent,
            'database': database_agent,
            'backend': backend_agent,
            'frontend': frontend_agent,
            'devops': devops_agent,
            'project_management': project_management_agent
        }
        self.response_optimizer = response_optimizer_agent
        self.request_analyzer = request_analyzer_agent
        self.logger = logging.getLogger(__name__)
        
        # Project file cache
        self.project_files: Dict[str, str] = {}
    
    def process_request(self, request_type: str, project_path: str, user_message: str) -> str:
        """Process user requests with intelligent agent selection"""
        try:
            # Validate inputs
            if not user_message or not isinstance(user_message, str):
                raise ValueError("User message must be a non-empty string")
                
            self.logger.info(f"Processing request for {project_path}")
            
            # Validate project path
            self.validate_project_path(project_path)
            
            # Get project files with content
            self.project_files = self.get_project_files_with_content(project_path)
            if not self.project_files:
                return "Nenhum arquivo relevante encontrado para análise no projeto."
            
            # Analyze request to determine which agents to use
            analysis = self.request_analyzer.analyze_request(user_message)
            required_agents = analysis['agents_to_use']
            context = analysis['context']
            
            self.logger.info(f"Required agents: {required_agents}")
            
            # Add project files to context
            context['project_files'] = self.project_files
            
            # Process with required agents
            responses = self._process_with_agents(
                required_agents,
                project_path,
                user_message,
                self.project_files,
                context
            )
            
            # If no responses were generated, return error message
            if not any(responses.values()):
                return "Não foi possível processar a solicitação. Por favor, tente novamente."
            
            # Optimize responses using the response optimizer
            if self.response_optimizer:
                try:
                    self.logger.info("Optimizing responses")
                    final_response = self.response_optimizer.optimize_responses(
                        responses,
                        user_message,
                        context
                    )
                    return final_response
                except Exception as e:
                    self.logger.error(f"Error optimizing responses: {str(e)}")
                    # If optimization fails, return the raw responses
                    return self._format_raw_responses(responses)
            else:
                # If no optimizer is available, format raw responses
                return self._format_raw_responses(responses)
                
        except ValueError as e:
            self.logger.error(f"Validation error: {str(e)}")
            raise IntegrationError(f"Erro de validação: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            raise IntegrationError(f"Erro ao processar solicitação: {str(e)}")
    
    def _process_with_agents(self, required_agents: List[str], project_path: str,
                           user_message: str, project_files: Dict[str, str],
                           context: Dict) -> Dict[str, str]:
        """Process the request with specified agents"""
        responses = {}
        errors = []
        
        with ThreadPoolExecutor() as executor:
            # Create tasks for required agents
            future_to_agent = {}
            for agent_name in required_agents:
                agent = self.agents.get(agent_name)
                if agent:  # Only process if agent exists
                    future = executor.submit(
                        self._execute_agent,
                        agent_name,
                        agent,
                        project_path,
                        user_message,
                        project_files,
                        context
                    )
                    future_to_agent[future] = agent_name
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    if result:
                        responses[agent_name] = result
                except Exception as e:
                    error_msg = f"Erro no agente {agent_name}: {str(e)}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
        
        # Add errors to responses if any occurred
        if errors:
            responses['Erros'] = "\n".join(errors)
        
        return responses
    
    def _execute_agent(self, agent_name: str, agent, project_path: str,
                      user_message: str, project_files: Dict[str, str],
                      context: Dict) -> Optional[str]:
        """Execute a single agent and return its response"""
        try:
            self.logger.info(f"Executing agent: {agent_name}")
            
            # Call the appropriate method based on agent type
            if hasattr(agent, 'analyze_code'):
                return agent.analyze_code(project_path, user_message)
            elif hasattr(agent, 'suggest_improvements'):
                return agent.suggest_improvements(project_path, user_message)
            elif hasattr(agent, 'analyze_database'):
                return agent.analyze_database(project_path, user_message)
            elif hasattr(agent, 'analyze_backend'):
                return agent.analyze_backend(project_path, user_message)
            elif hasattr(agent, 'analyze_frontend'):
                return agent.analyze_frontend(project_path, user_message)
            elif hasattr(agent, 'analyze_devops'):
                return agent.analyze_devops(project_path, user_message)
            elif hasattr(agent, 'analyze_project'):
                return agent.analyze_project(project_path, user_message)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error executing agent {agent_name}: {str(e)}")
            raise
    
    def _format_raw_responses(self, responses: Dict[str, str]) -> str:
        """Format raw responses from agents when optimizer is not available"""
        formatted_response = []
        
        for agent_name, response in responses.items():
            if response and agent_name != 'Erros':
                formatted_response.extend([
                    f"## {agent_name}",
                    response,
                    "---\n"
                ])
        
        # Add errors at the end if any
        if 'Erros' in responses:
            formatted_response.extend([
                "## Erros Encontrados",
                responses['Erros'],
                "---\n"
            ])
        
        return "\n".join(formatted_response)
    
    def validate_project_path(self, project_path: str) -> None:
        """Validate if the project path exists and is accessible"""
        try:
            if not project_path or not isinstance(project_path, str):
                raise ValueError("Project path must be a non-empty string")
            
            path = Path(project_path)
            if not path.exists():
                raise ValueError(f"Project path does not exist: {project_path}")
            if not path.is_dir():
                raise ValueError(f"Project path is not a directory: {project_path}")
                
            # Check if directory is readable
            try:
                files = list(path.iterdir())
                self.logger.info(f"Found {len(files)} files in directory")
            except PermissionError:
                raise ValueError(f"Cannot access directory: {project_path}")
                
        except Exception as e:
            raise ValueError(f"Error validating project path: {str(e)}")
    
    def get_project_files_with_content(self, project_path: str) -> Dict[str, str]:
        """Get dictionary of project files and their contents"""
        try:
            files_content = {}
            path = Path(project_path)
            
            # File extensions to analyze
            code_extensions = {'.py', '.js', '.html', '.css', '.json', '.yml', '.yaml', '.md',
                             '.sql', '.env', '.docker', '.sh', '.conf', '.xml'}
            
            # Directories to ignore
            ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.env'}
            
            for item in path.rglob('*'):
                # Skip ignored directories
                if any(ignore_dir in item.parts for ignore_dir in ignore_dirs):
                    continue
                    
                # Include only files with relevant extensions
                if item.is_file() and item.suffix in code_extensions:
                    try:
                        with open(item, 'r', encoding='utf-8') as f:
                            content = f.read()
                            relative_path = str(item.relative_to(path))
                            files_content[relative_path] = content
                    except Exception as e:
                        self.logger.warning(f"Could not read file {item}: {str(e)}")
            
            self.logger.info(f"Found {len(files_content)} relevant files to analyze")
            return files_content
            
        except Exception as e:
            raise IntegrationError(f"Error getting project files: {str(e)}")
    
    def get_project_files(self, project_path: str) -> list:
        """Get list of relevant files in the project"""
        try:
            path = Path(project_path)
            files = []
            
            # File extensions to analyze
            code_extensions = {'.py', '.js', '.html', '.css', '.json', '.yml', '.yaml', '.md',
                             '.sql', '.env', '.docker', '.sh', '.conf', '.xml'}
            
            # Directories to ignore
            ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.env'}
            
            for item in path.rglob('*'):
                # Skip ignored directories
                if any(ignore_dir in item.parts for ignore_dir in ignore_dirs):
                    continue
                    
                # Include only files with relevant extensions
                if item.is_file() and item.suffix in code_extensions:
                    files.append(item)
            
            self.logger.info(f"Found {len(files)} relevant files to analyze")
            return files
            
        except Exception as e:
            raise IntegrationError(f"Error getting project files: {str(e)}")
