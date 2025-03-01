# agents/response_optimizer_agent.py

import logging
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class ConversationContext:
    """Store context about the current conversation"""
    last_topic: str = None
    last_files_discussed: List[str] = field(default_factory=list)
    last_code_suggestions: Dict[str, str] = field(default_factory=dict)
    conversation_history: List[Dict] = field(default_factory=list)
    
    def add_message(self, message: str, response: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            'message': message,
            'response': response
        })
    
    def get_last_context(self) -> Optional[Dict]:
        """Get context from last conversation"""
        if not self.conversation_history:
            return None
        return self.conversation_history[-1]

class ResponseOptimizerAgent:
    def __init__(self, model):
        if not model:
            raise ValueError("Model is required")
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.context = ConversationContext()
    
    def optimize_responses(self, responses: Dict[str, str], user_message: str, context: Dict) -> str:
        """
        Optimize and combine responses from agents into a single coherent response
        
        Args:
            responses: Dictionary with agent names as keys and their responses as values
            user_message: Original user request
            context: Additional context about the request
        """
        try:
            self.logger.info("Starting response optimization")
            
            # Update conversation context
            self._update_context(user_message, responses, context)
            
            # Create optimization prompt
            prompt = self._create_optimization_prompt(responses, user_message, context)
            
            # Generate optimized response
            optimized_response = self.model.generate(prompt)
            
            # Post-process the response to ensure proper code block formatting
            formatted_response = self._format_response(optimized_response)
            
            # Store the optimized response
            self.context.add_message(user_message, formatted_response)
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"Error optimizing responses: {str(e)}")
            raise Exception(f"Erro ao otimizar respostas: {str(e)}")
    
    def _format_response(self, response: str) -> str:
        """Format response ensuring all file contents are in code blocks"""
        try:
            # Pattern to match file paths and their content
            file_pattern = r'(?:arquivo|file|path):\s*([^\n]+)|(?:em|in|at)\s+`([^`]+)`'
            
            lines = response.split('\n')
            formatted_lines = []
            in_code_block = False
            current_file = None
            current_block = []
            
            for line in lines:
                # Check for file paths
                file_match = re.search(file_pattern, line, re.IGNORECASE)
                if file_match:
                    # Close previous code block if any
                    if in_code_block and current_block:
                        formatted_lines.append('```')
                        in_code_block = False
                    
                    # Get file path from either group
                    current_file = file_match.group(1) or file_match.group(2)
                    formatted_lines.append(f"\n**{current_file}**:")
                    continue
                
                # Check for code block markers
                if line.strip().startswith('```'):
                    if not in_code_block:
                        # Starting new code block
                        in_code_block = True
                        current_block = []
                        # Keep language specification if present
                        formatted_lines.append(line)
                    else:
                        # Ending code block
                        in_code_block = False
                        # Add block content and closing marker
                        formatted_lines.extend(current_block)
                        formatted_lines.append(line)
                        current_block = []
                elif in_code_block:
                    # Collect code lines
                    current_block.append(line)
                else:
                    # Check if this line looks like code but isn't in a block
                    if self._looks_like_code(line) and current_file:
                        if not in_code_block:
                            # Start a new code block with appropriate language
                            lang = self._detect_language(current_file)
                            formatted_lines.append(f"```{lang}")
                            in_code_block = True
                        current_block.append(line)
                    else:
                        # Regular text
                        formatted_lines.append(line)
            
            # Close any remaining code block
            if in_code_block and current_block:
                formatted_lines.extend(current_block)
                formatted_lines.append('```')
            
            # Join lines and clean up
            formatted_response = '\n'.join(formatted_lines)
            
            # Remove empty code blocks
            formatted_response = re.sub(r'```\w*\s*```\n?', '', formatted_response)
            
            # Fix spacing around code blocks
            formatted_response = re.sub(r'```(\w+)\n\n', r'```\1\n', formatted_response)
            formatted_response = re.sub(r'\n\n```', r'\n```', formatted_response)
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"Error formatting response: {str(e)}")
            return response
    
    def _looks_like_code(self, line: str) -> bool:
        """Check if a line looks like code"""
        code_patterns = [
            r'^\s*<[^>]+>',  # HTML tags
            r'^\s*[.#][\w-]+\s*{',  # CSS selectors
            r'^\s*function\s+\w+\s*\(',  # JavaScript functions
            r'^\s*const\s+|^\s*let\s+|^\s*var\s+',  # JavaScript variables
            r'^\s*import\s+|^\s*export\s+',  # JavaScript imports/exports
            r'^\s*class\s+\w+',  # Class definitions
            r'^\s*def\s+\w+\s*\(',  # Python functions
            r'^\s*@\w+',  # Decorators
            r'^\s*return\s+',  # Return statements
            r'^\s*if\s+|^\s*else\s+|^\s*elif\s+',  # Control structures
            r'^\s*try\s*:|^\s*except\s+',  # Exception handling
            r'^\s*\w+\s*=\s*',  # Assignments
        ]
        return any(re.match(pattern, line) for pattern in code_patterns)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect language based on file extension"""
        ext = file_path.lower().split('.')[-1]
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'html': 'html',
            'css': 'css',
            'scss': 'scss',
            'json': 'json',
            'md': 'markdown',
            'sql': 'sql',
            'sh': 'bash',
            'yml': 'yaml',
            'yaml': 'yaml',
            'xml': 'xml'
        }
        return language_map.get(ext, 'plaintext')
    
    def _update_context(self, user_message: str, responses: Dict[str, str], context: Dict):
        """Update conversation context with new information"""
        # Update last topic if available
        if 'analysis_type' in context:
            self.context.last_topic = context['analysis_type']
        
        # Update files discussed
        if 'project_files' in context:
            self.context.last_files_discussed = list(context['project_files'].keys())
        
        # Extract code suggestions from responses
        code_blocks = self._extract_code_blocks(responses)
        if code_blocks:
            self.context.last_code_suggestions = code_blocks
    
    def _extract_code_blocks(self, responses: Dict[str, str]) -> Dict[str, str]:
        """Extract code blocks and their file paths from responses"""
        code_blocks = {}
        file_pattern = r'(?:arquivo|file|path):\s*([^\n]+)'
        
        for response in responses.values():
            if not response:
                continue
            
            lines = response.split('\n')
            current_file = None
            in_code_block = False
            current_block = []
            
            for line in lines:
                # Check for file path
                file_match = re.search(file_pattern, line, re.IGNORECASE)
                if file_match:
                    current_file = file_match.group(1).strip()
                    continue
                
                # Check for code block markers
                if line.strip().startswith('```'):
                    if not in_code_block:
                        in_code_block = True
                    else:
                        if current_file and current_block:
                            code_blocks[current_file] = '\n'.join(current_block)
                        in_code_block = False
                        current_block = []
                elif in_code_block:
                    current_block.append(line)
        
        return code_blocks
    
    def _create_optimization_prompt(self, responses: Dict[str, str], user_message: str, context: Dict) -> str:
        """Create a context-aware prompt for response optimization"""
        needs_code = context.get('needs_code_examples', False)
        analysis = context.get('analysis', '')
        refers_to_previous = context.get('refers_to_previous', False)
        previous_context = self.context.get_last_context()
        
        prompt = f"""
        Otimize e combine as seguintes respostas em uma única resposta coerente.

        Solicitação Original:
        {user_message}

        {'Contexto Anterior:' if refers_to_previous else ''}
        {'Última Solicitação: ' + previous_context['message'] if previous_context else ''}
        {'Última Resposta: ' + previous_context['response'] if previous_context else ''}

        Análise da Solicitação:
        {analysis}

        Respostas dos Agentes:
        """
        
        # Add each agent's response
        for agent_name, response in responses.items():
            if response and agent_name != 'Erros':
                prompt += f"\n### {agent_name}:\n{response}\n"
        
        # Add any errors at the end
        if 'Erros' in responses:
            prompt += f"\n### Erros Encontrados:\n{responses['Erros']}\n"
        
        prompt += f"""
        Por favor, crie uma única resposta otimizada que:
        1. Responda DIRETAMENTE à solicitação do usuário
        2. {'Se refira especificamente ao contexto da conversa anterior' if refers_to_previous else 'Foque no contexto atual da solicitação'}
        3. {'Forneça TODOS os códigos necessários em blocos de código completos' if needs_code else 'Seja concisa e direta'}
        4. Mantenha apenas as informações relevantes para a solicitação
        5. Use uma linguagem clara e profissional em português do Brasil
        
        Regras importantes para código:
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
        """
        
        return prompt
