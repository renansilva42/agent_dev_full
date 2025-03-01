# tests/test_base_agent.py
import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from pathlib import Path
from agents.base_agent import BaseAgent

class TestBaseAgent(unittest.TestCase):
    """Testes para a classe BaseAgent"""
    
    def setUp(self):
        """Configuração para cada teste"""
        self.model_mock = MagicMock()
        
        # Criar uma classe concreta para testar
        class ConcreteAgent(BaseAgent):
            def analyze(self, project_path, user_request):
                return f"Análise de {project_path} com requisição: {user_request}"
        
        self.agent = ConcreteAgent(self.model_mock)
        
        # Criar diretório temporário para testes
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        
        # Criar alguns arquivos para teste
        self.create_test_files()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.temp_dir.cleanup()
    
    def create_test_files(self):
        """Cria arquivos de teste no diretório temporário"""
        # Criar arquivo Python
        with open(os.path.join(self.project_path, 'test.py'), 'w') as f:
            f.write('print("Hello, World!")')
        
        # Criar arquivo JavaScript
        with open(os.path.join(self.project_path, 'test.js'), 'w') as f:
            f.write('console.log("Hello, World!");')
        
        # Criar diretório node_modules para testar ignorar
        node_modules_dir = os.path.join(self.project_path, 'node_modules')
        os.makedirs(node_modules_dir, exist_ok=True)
        with open(os.path.join(node_modules_dir, 'ignore.js'), 'w') as f:
            f.write('// Este arquivo deve ser ignorado')
    
    def test_get_project_files(self):
        """Testa o método get_project_files"""
        # Definir extensões para teste
        extensions = {'.py': 'Python', '.js': 'JavaScript'}
        
        # Obter arquivos
        files = self.agent.get_project_files(self.project_path, extensions)
        
        # Verificar se encontrou os arquivos corretos
        self.assertEqual(len(files), 2)
        
        # Verificar se os arquivos têm as informações corretas
        python_file = next((f for f in files if f['extension'] == '.py'), None)
        js_file = next((f for f in files if f['extension'] == '.js'), None)
        
        self.assertIsNotNone(python_file)
        self.assertIsNotNone(js_file)
        self.assertEqual(python_file['name'], 'test.py')
        self.assertEqual(js_file['name'], 'test.js')
        self.assertEqual(python_file['language'], 'Python')
        self.assertEqual(js_file['language'], 'JavaScript')
    
    def test_ignore_directories(self):
        """Testa se diretórios ignorados são realmente ignorados"""
        # Definir extensões para teste
        extensions = {'.js': 'JavaScript'}
        
        # Obter arquivos
        files = self.agent.get_project_files(self.project_path, extensions)
        
        # Verificar se apenas um arquivo JS foi encontrado (o que não está em node_modules)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], 'test.js')
        
        # Verificar se não há arquivos de node_modules
        node_modules_files = [f for f in files if 'node_modules' in f['path']]
        self.assertEqual(len(node_modules_files), 0)
    
    def test_create_overview(self):
        """Testa o método create_overview"""
        # Criar lista de arquivos para teste
        files = [
            {'path': '/path/to/file1.py', 'name': 'file1.py', 'extension': '.py', 
             'language': 'Python', 'relative_path': 'file1.py'},
            {'path': '/path/to/file2.js', 'name': 'file2.js', 'extension': '.js', 
             'language': 'JavaScript', 'relative_path': 'file2.js'},
            {'path': '/path/to/file3.py', 'name': 'file3.py', 'extension': '.py', 
             'language': 'Python', 'relative_path': 'file3.py'}
        ]
        
        # Gerar visão geral
        overview = self.agent.create_overview(files)
        
        # Verificar se a visão geral contém as informações corretas
        self.assertIn("Estrutura do Projeto:", overview)
        self.assertIn("Arquivos Python (2):", overview)
        self.assertIn("Arquivos JavaScript (1):", overview)
        self.assertIn("  - file1.py", overview)
        self.assertIn("  - file3.py", overview)
        self.assertIn("  - file2.js", overview)
    
    def test_read_files(self):
        """Testa o método read_files"""
        # Definir extensões para teste
        extensions = {'.py': 'Python', '.js': 'JavaScript'}
        
        # Obter arquivos
        files = self.agent.get_project_files(self.project_path, extensions)
        
        # Ler conteúdo dos arquivos
        content = self.agent.read_files(files)
        
        # Verificar se o conteúdo contém os arquivos corretos
        self.assertIn("Arquivo: test.py", content)
        self.assertIn("Linguagem: Python", content)
        self.assertIn('print("Hello, World!")', content)
        
        self.assertIn("Arquivo: test.js", content)
        self.assertIn("Linguagem: JavaScript", content)
        self.assertIn('console.log("Hello, World!");', content)

# tests/test_integration_layer.py
import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from pathlib import Path
from integration.integration_layer import IntegrationLayer, IntegrationError

class TestIntegrationLayer(unittest.TestCase):
    """Testes para a classe IntegrationLayer"""
    
    def setUp(self):
        """Configuração para cada teste"""
        # Criar mocks para os agentes
        self.code_analysis_agent = MagicMock()
        self.project_improvement_agent = MagicMock()
        self.database_agent = MagicMock()
        self.backend_agent = MagicMock()
        self.frontend_agent = MagicMock()
        self.devops_agent = MagicMock()
        self.project_management_agent = MagicMock()
        self.response_optimizer_agent = MagicMock()
        self.request_analyzer_agent = MagicMock()
        
        # Configurar comportamento do request_analyzer_agent
        self.request_analyzer_agent.analyze_request.return_value = {
            'agents_to_use': ['code_analysis'],
            'analysis_type': 'single',
            'context': {}
        }
        
        # Configurar comportamento do code_analysis_agent
        self.code_analysis_agent.analyze.return_value = "Análise de código concluída"
        
        # Criar camada de integração
        self.integration_layer = IntegrationLayer(
            code_analysis_agent=self.code_analysis_agent,
            project_improvement_agent=self.project_improvement_agent,
            database_agent=self.database_agent,
            backend_agent=self.backend_agent,
            frontend_agent=self.frontend_agent,
            devops_agent=self.devops_agent,
            project_management_agent=self.project_management_agent,
            response_optimizer_agent=self.response_optimizer_agent,
            request_analyzer_agent=self.request_analyzer_agent
        )
        
        # Criar diretório temporário para testes
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        
        # Criar alguns arquivos para teste
        self.create_test_files()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.temp_dir.cleanup()
    
    def create_test_files(self):
        """Cria arquivos de teste no diretório temporário"""
        # Criar arquivo Python
        with open(os.path.join(self.project_path, 'test.py'), 'w') as f:
            f.write('print("Hello, World!")')
        
        # Criar arquivo JavaScript
        with open(os.path.join(self.project_path, 'test.js'), 'w') as f:
            f.write('console.log("Hello, World!");')
    
    def test_process_request_with_code_analysis(self):
        """Testa o processamento de uma solicitação de análise de código"""
        # Configurar comportamento do request_analyzer_agent
        self.request_analyzer_agent.analyze_request.return_value = {
            'agents_to_use': ['code_analysis'],
            'analysis_type': 'single',
            'context': {}
        }
        
        # Processar solicitação
        response = self.integration_layer.process_request(
            "chat", self.project_path, "Analise o código deste projeto"
        )
        
        # Verificar se o agente correto foi chamado
        self.code_analysis_agent.analyze.assert_called_once()
        self.assertEqual(response, "Análise de código concluída")
    
    def test_process_request_with_multiple_agents(self):
        """Testa o processamento de uma solicitação que requer múltiplos agentes"""
        # Configurar comportamento do request_analyzer_agent
        self.request_analyzer_agent.analyze_request.return_value = {
            'agents_to_use': ['code_analysis', 'project_improvement'],
            'analysis_type': 'multiple',
            'context': {}
        }
        
        # Configurar comportamento dos agentes
        self.code_analysis_agent.analyze.return_value = "Análise de código concluída"
        self.project_improvement_agent.suggest_improvements.return_value = "Sugestões de melhoria concluídas"
        
        # Configurar comportamento do response_optimizer_agent
        self.response_optimizer_agent.optimize_response.return_value = "Resposta otimizada"
        
        # Processar solicitação
        response = self.integration_layer.process_request(
            "chat", self.project_path, "Analise e melhore o código deste projeto"
        )
        
        # Verificar se os agentes corretos foram chamados
        self.code_analysis_agent.analyze.assert_called_once()
        self.project_improvement_agent.suggest_improvements.assert_called_once()
        
        # Verificar se o otimizador de resposta foi chamado
        self.response_optimizer_agent.optimize_response.assert_called_once()
        
        # Verificar resposta
        self.assertEqual(response, "Resposta otimizada")
    
    def test_validate_project_path_invalid(self):
        """Testa a validação de um caminho de projeto inválido"""
        # Testar com caminho vazio
        with self.assertRaises(ValueError):
            self.integration_layer.validate_project_path("")
        
        # Testar com caminho inexistente
        with self.assertRaises(ValueError):
            self.integration_layer.validate_project_path("/caminho/inexistente")
        
        # Testar com arquivo em vez de diretório
        file_path = os.path.join(self.project_path, 'test.py')
        with self.assertRaises(ValueError):
            self.integration_layer.validate_project_path(file_path)
    
    def test_validate_project_path_valid(self):
        """Testa a validação de um caminho de projeto válido"""
        # Não deve lançar exceção
        try:
            self.integration_layer.validate_project_path(self.project_path)
        except ValueError:
            self.fail("validate_project_path() lançou ValueError inesperadamente!")