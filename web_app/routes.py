# web_app/routes.py
import os
import logging
from pathlib import Path
from flask import request, jsonify, session, current_app, send_from_directory
from integration.integration_layer import IntegrationError

def configure_routes(app, integration_layer):
    """Configura as rotas da aplicação Flask"""
    logger = logging.getLogger(__name__)
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve arquivos estáticos"""
        try:
            logger.info(f"Servindo arquivo estático: {filename}")
            static_dir = current_app.static_folder
            return send_from_directory(static_dir, filename)
        except Exception as e:
            logger.error(f"Erro ao servir arquivo estático {filename}: {str(e)}")
            return "Erro ao servir arquivo", 500
    
    @app.route('/')
    def index():
        """Serve a página principal"""
        try:
            logger.info("Servindo página principal")
            static_dir = current_app.static_folder
            return send_from_directory(static_dir, 'index.html')
        except Exception as e:
            logger.error(f"Erro ao servir página principal: {str(e)}")
            return "Erro ao servir página", 500
    
    @app.route('/set_project_path', methods=['POST'])
    def set_project_path():
        """Define o caminho do projeto na sessão"""
        try:
            if not request.is_json:
                logger.warning("Requisição sem JSON recebida em /set_project_path")
                return jsonify({"error": "Requisição deve ser JSON"}), 400
            
            data = request.get_json()
            project_path = data.get('project_path')
            
            if not project_path:
                logger.warning("Caminho do projeto não fornecido")
                return jsonify({"error": "Caminho do projeto não fornecido"}), 400
            
            logger.info(f"Tentando definir caminho do projeto: {project_path}")
            
            # Verificar se o caminho existe
            path = Path(project_path)
            if not path.exists():
                # Tentar encontrar em locais comuns
                common_locations = [
                    Path.home() / 'Desktop',
                    Path.home() / 'Documents',
                    Path.home() / 'Projects',
                    Path.home()
                ]
                
                for location in common_locations:
                    test_path = location / project_path
                    if test_path.exists() and test_path.is_dir():
                        path = test_path
                        break
                else:
                    logger.warning(f"Caminho do projeto não encontrado: {project_path}")
                    return jsonify({"error": f"Caminho do projeto não encontrado: {project_path}"}), 400
            
            # Verificar se é um diretório
            if not path.is_dir():
                logger.warning(f"Caminho não é um diretório: {path}")
                return jsonify({"error": f"Caminho não é um diretório: {path}"}), 400
            
            # Armazenar na sessão
            session['project_path'] = str(path)
            logger.info(f"Caminho do projeto definido: {path}")
            
            return jsonify({"message": "Caminho do projeto definido com sucesso", "path": str(path)}), 200
            
        except Exception as e:
            logger.error(f"Erro ao definir caminho do projeto: {str(e)}")
            return jsonify({"error": f"Erro ao definir caminho do projeto: {str(e)}"}), 500
    
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