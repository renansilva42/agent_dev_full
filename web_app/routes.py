from flask import Blueprint, render_template, request, jsonify, current_app
from pathlib import Path
import logging
import os


# Configuração do logger
logger = logging.getLogger(__name__)

# Criação do blueprint
routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    """Rota principal que renderiza a página inicial."""
    logger.info("Servindo página principal")
    return render_template('index.html')

@routes.route('/set_project_path', methods=['POST'])
def set_project_path():
    """
    Define o caminho do projeto para análise.
    Aceita um caminho e verifica se ele existe.
    """
    data = request.json
    project_path = data.get('project_path', '')
    
    logger.info(f"Tentando definir caminho do projeto: {project_path}")
    
    # Verifica se o caminho está vazio
    if not project_path:
        logger.warning("Caminho do projeto vazio")
        return jsonify({"error": "Caminho do projeto não pode ser vazio"}), 400
    
    # Cria um objeto Path para o caminho fornecido
    path = Path(project_path)
    
    # Verifica se o caminho existe diretamente
    if path.exists() and path.is_dir():
        current_app.config['PROJECT_PATH'] = str(path.absolute())
        logger.info(f"Caminho do projeto definido: {current_app.config['PROJECT_PATH']}")
        return jsonify({"success": True, "path": current_app.config['PROJECT_PATH']}), 200
    
    # MODIFICAÇÃO: Tenta resolver caminhos relativos
    cwd = Path.cwd()
    relative_path = cwd / project_path
    if relative_path.exists() and relative_path.is_dir():
        current_app.config['PROJECT_PATH'] = str(relative_path.absolute())
        logger.info(f"Caminho relativo do projeto definido: {current_app.config['PROJECT_PATH']}")
        return jsonify({"success": True, "path": current_app.config['PROJECT_PATH']}), 200
    
    # MODIFICAÇÃO: Tenta resolver caminho pai (..)
    if project_path == '..' or project_path == '../':
        parent_dir = cwd.parent
        if parent_dir.exists() and parent_dir.is_dir():
            current_app.config['PROJECT_PATH'] = str(parent_dir.absolute())
            logger.info(f"Caminho pai definido: {current_app.config['PROJECT_PATH']}")
            return jsonify({"success": True, "path": current_app.config['PROJECT_PATH']}), 200
    
    # Tenta encontrar o caminho em locais comuns
    common_locations = [
        Path.cwd(),  # Diretório atual
        Path.cwd().parent,  # Diretório pai
        Path.home() / 'Desktop',
        Path.home() / 'Documents',
        Path.home() / 'Projects',
        Path.home() / 'VS Code Workspace',  # Adicionado com base nos logs
        Path.home()
    ]
    
    for location in common_locations:
        test_path = location / project_path
        if test_path.exists() and test_path.is_dir():
            current_app.config['PROJECT_PATH'] = str(test_path.absolute())
            logger.info(f"Caminho do projeto encontrado em local comum: {current_app.config['PROJECT_PATH']}")
            return jsonify({"success": True, "path": current_app.config['PROJECT_PATH']}), 200
    
    # MODIFICAÇÃO: Imprime informações de debug para ajudar a diagnosticar o problema
    logger.warning(f"Caminho do projeto não encontrado: {project_path}")
    logger.info(f"Diretório atual: {os.getcwd()}")
    logger.info(f"Locais verificados: {[str(loc) for loc in common_locations]}")
    
    return jsonify({"error": f"Caminho do projeto não encontrado: {project_path}"}), 400

    
    @app.route('/chat', methods=['POST'])
    def chat():
        """Processa mensagens de chat"""
        try:
            if not request.is_json:
                logger.warning("Requisição sem JSON recebida em /chat")
                return jsonify({"error": "Requisição deve ser JSON"}), 400
            
            data = request.get_json()
            message = data.get('message')
            
            if not message:
                logger.warning("Mensagem não fornecida")
                return jsonify({"error": "Mensagem não fornecida"}), 400
            
            # Verificar se o caminho do projeto está definido
            project_path = session.get('project_path')
            if not project_path:
                logger.warning("Caminho do projeto não definido na sessão")
                return jsonify({"error": "Caminho do projeto não definido. Use /set_project_path primeiro."}), 400
            
            # Verificar se o diretório existe
            path = Path(project_path)
            if not path.exists() or not path.is_dir():
                logger.warning(f"Diretório do projeto não existe: {project_path}")
                return jsonify({"error": f"Diretório do projeto não existe: {project_path}"}), 400
            
            logger.info(f"Processando mensagem para projeto: {project_path}")
            
            # Processar a mensagem
            response = integration_layer.process_request("chat", project_path, message)
            
            return jsonify({"response": response}), 200
            
        except IntegrationError as e:
            logger.error(f"Erro de integração: {str(e)}")
            return jsonify({"error": f"Erro de integração: {str(e)}"}), 500
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return jsonify({"error": f"Erro ao processar mensagem: {str(e)}"}), 500