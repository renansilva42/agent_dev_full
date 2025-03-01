# model/transformer_model.py

import os
import re
from typing import Dict, List, Optional
import openai
from dotenv import load_dotenv

class OpenAIError(Exception):
    """Custom exception for OpenAI API errors"""
    pass

class TransformerModel:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = api_key
        
        # Model configuration
        self.model_name = "gpt-4o-mini-2024-07-18"
        self.max_tokens = 4000  # Response token limit
        self.max_input_tokens = 150000  # Input token limit
        self.chunk_size = 50000  # Size of each chunk for processing
        
        # Code block tracking
        self.current_file_content: Dict[str, str] = {}
        self.modified_files: Dict[str, str] = {}
    
    def generate(self, prompt: str, project_files: Optional[Dict[str, str]] = None) -> str:
        """
        Generate response with code interpretation capabilities
        
        Args:
            prompt: The prompt to send to the model
            project_files: Optional dict of project files and their contents
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Invalid prompt: must be a non-empty string")
        
        try:
            # Store project files for context
            if project_files:
                self.current_file_content = project_files
            
            # Add code interpretation instructions
            code_prompt = self._create_code_prompt(prompt)
            
            # Split content into chunks if too large
            chunks = self._chunk_content(code_prompt)
            responses = []
            
            # Process each chunk
            for chunk in chunks:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": """Você é um assistente especializado em análise e melhoria de código.
                            
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
                        },
                        {"role": "user", "content": chunk}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=0.7
                )
                
                if response.choices:
                    responses.append(response.choices[0].message['content'].strip())
            
            # Combine and format responses
            combined_response = " ".join(responses)
            formatted_response = self._format_code_blocks(combined_response)
            
            return formatted_response
            
        except Exception as e:
            raise OpenAIError(f"Erro na API do OpenAI: {str(e)}")
    
    def _chunk_content(self, content: str) -> List[str]:
        """Split content into manageable chunks"""
        words = content.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word.split())
            if current_size + word_size > self.chunk_size:
                # Add current chunk to list
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        # Add last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _create_code_prompt(self, prompt: str) -> str:
        """Create a prompt with code interpretation context"""
        code_context = "\n\nArquivos do Projeto:\n"
        
        if self.current_file_content:
            # Calculate total size of file contents
            total_size = sum(len(content.split()) for content in self.current_file_content.values())
            
            # If total size is too large, only include relevant files
            if total_size > self.max_input_tokens:
                relevant_files = self._get_relevant_files(prompt)
                for file_path in relevant_files:
                    if file_path in self.current_file_content:
                        content = self.current_file_content[file_path]
                        code_context += f"\n[{file_path}]\n```\n{content}\n```\n"
            else:
                for file_path, content in self.current_file_content.items():
                    code_context += f"\n[{file_path}]\n```\n{content}\n```\n"
        
        return f"""
        {prompt}

        {code_context}

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
    
    def _get_relevant_files(self, prompt: str) -> List[str]:
        """Determine which files are most relevant to the prompt"""
        relevant_files = []
        
        # Keywords to look for in filenames based on prompt
        keywords = set(prompt.lower().split())
        
        for file_path in self.current_file_content.keys():
            # Check if any keyword appears in the file path
            if any(keyword in file_path.lower() for keyword in keywords):
                relevant_files.append(file_path)
            
            # If file has specific extensions that might be relevant
            if any(ext in file_path.lower() for ext in ['.html', '.css', '.js', '.py']):
                relevant_files.append(file_path)
        
        return list(set(relevant_files))  # Remove duplicates
    
    def _format_code_blocks(self, response: str) -> str:
        """Format code blocks with file paths and proper markdown"""
        try:
            # Pattern to match file paths
            file_pattern = r'\[([^\]]+)\]'
            
            lines = response.split('\n')
            formatted_lines = []
            in_code_block = False
            current_file = None
            current_block = []
            
            for line in lines:
                # Check for file paths
                file_match = re.search(file_pattern, line)
                if file_match and not in_code_block:
                    # Close previous code block if any
                    if current_block:
                        formatted_lines.append('```')
                        current_block = []
                    
                    current_file = file_match.group(1)
                    formatted_lines.append(f"\n**{current_file}**:")
                    continue
                
                # Check for code block markers
                if line.strip().startswith('```'):
                    if not in_code_block:
                        # Starting new code block
                        in_code_block = True
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
                    # Regular text
                    formatted_lines.append(line)
            
            # Close any remaining code block
            if current_block:
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
            print(f"Error formatting code blocks: {str(e)}")
            return response
