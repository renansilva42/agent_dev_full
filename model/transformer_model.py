# model/transformer_model.py
import os
import re
import hashlib
import json
from typing import Dict, List, Optional
from pathlib import Path
import openai
from dotenv import load_dotenv

class CacheManager:
    """Gerencia cache de respostas para reduzir chamadas à API"""
    
    def __init__(self, cache_dir=".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, prompt: str) -> str:
        """Gera uma chave de cache baseada no prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get_from_cache(self, key: str) -> Optional[str]:
        """Recupera resposta do cache se existir"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('response')
            except Exception:
                return None
        return None
    
    def save_to_cache(self, key: str, response: str) -> None:
        """Salva resposta no cache"""
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({'response': response}, f)
        except Exception:
            pass

class OpenAIError(Exception):
    """Exceção personalizada para erros da API OpenAI"""
    pass

class TransformerModel:
    """Modelo para geração de respostas usando a API OpenAI"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        
        openai.api_key = self.api_key
        
        # Configurações do modelo
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        self.max_input_tokens = int(os.getenv("MAX_INPUT_TOKENS", "4000"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "2000"))
        
        # Cache para respostas
        self.cache_manager = CacheManager()
        
        # Rastreamento de arquivos
        self.current_file_content = {}
        self.modified_files = {}
    
    def generate(self, prompt: str, project_files: Optional[Dict[str, str]] = None) -> str:
        """Gera uma resposta com base no prompt e arquivos do projeto"""
        if not prompt:
            raise ValueError("Prompt não pode estar vazio")
        
        # Verificar cache primeiro
        cache_key = self.cache_manager.get_cache_key(prompt)
        cached_response = self.cache_manager.get_from_cache(cache_key)
        if cached_response:
            return cached_response
        
        # Armazenar arquivos do projeto para contexto
        if project_files:
            self.current_file_content = project_files
        
        try:
            # Criar prompt de código e dividir em chunks
            code_prompt = self._create_code_prompt(prompt)
            chunks = self._chunk_content(code_prompt)
            
            responses = []
            for i, chunk in enumerate(chunks):
                try:
                    # Usar a versão correta da API OpenAI (0.28.1)
                    response = openai.ChatCompletion.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Você é um assistente especializado em análise de código."},
                            {"role": "user", "content": chunk}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=0.2,
                        top_p=0.95,
                        frequency_penalty=0,
                        presence_penalty=0
                    )
                    
                    # Extrair resposta
                    response_text = response.choices[0].message.content
                    responses.append(response_text)
                    
                except Exception as e:
                    raise OpenAIError(f"OpenAI API error: {str(e)}")
            
            # Combinar e formatar respostas
            combined_response = " ".join(responses)
            formatted_response = self._format_code_blocks(combined_response)
            
            # Salvar no cache
            self.cache_manager.save_to_cache(cache_key, formatted_response)
            
            return formatted_response
            
        except Exception as e:
            if isinstance(e, OpenAIError):
                raise e
            raise OpenAIError(f"Error: {str(e)}")
    
    # [Outros métodos existentes permanecem iguais]