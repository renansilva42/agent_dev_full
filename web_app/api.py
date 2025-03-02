# web_app/api.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from models.project import Project
from models.analysis import Analysis
from database import db
import os
from pathlib import Path
import logging

api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    """Retorna todos os projetos do usuário"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'path': p.path,
        'description': p.description,
        'created_at': p.created_at.isoformat()
    } for p in projects])

@api.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """Cria um novo projeto"""
    data = request.json
    
    # Validar caminho do projeto
    path = Path(data['path']).resolve()
    if not path.exists() or not path.is_dir():
        return jsonify({'error': 'Caminho inválido ou não é um diretório'}), 400
    
    project = Project(
        name=data['name'],
        path=str(path),
        description=data.get('description', ''),
        user_id=current_user.id
    )
    
    try:
        db.session.add(project)
        db.session.commit()
        return jsonify({
            'id': project.id,
            'name': project.name,
            'path': project.path,
            'description': project.description,
            'created_at': project.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar projeto: {str(e)}")
        return jsonify({'error': 'Erro ao criar projeto'}), 500

@api.route('/api/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """Retorna detalhes de um projeto específico"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': project.id,
        'name': project.name,
        'path': project.path,
        'description': project.description,
        'created_at': project.created_at.isoformat()
    })

@api.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """Atualiza um projeto existente"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    if 'name' in data:
        project.name = data['name']
    
    if 'description' in data:
        project.description = data['description']
    
    if 'path' in data:
        path = Path(data['path']).resolve()
        if not path.exists() or not path.is_dir():
            return jsonify({'error': 'Caminho inválido ou não é um diretório'}), 400
        project.path = str(path)
    
    try:
        db.session.commit()
        return jsonify({
            'id': project.id,
            'name': project.name,
            'path': project.path,
            'description': project.description,
            'created_at': project.created_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar projeto: {str(e)}")
        return jsonify({'error': 'Erro ao atualizar projeto'}), 500

@api.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """Exclui um projeto"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Projeto excluído com sucesso'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir projeto: {str(e)}")
        return jsonify({'error': 'Erro ao excluir projeto'}), 500

@api.route('/api/projects/<int:project_id>/analyze', methods=['POST'])
@login_required
def analyze_project(project_id):
    """Analisa um projeto específico"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    analysis_type = data.get('type', 'general')
    user_message = data.get('message', '')
    
    try:
        # Obter o agente apropriado
        integration_layer = current_app.config['INTEGRATION_LAYER']
        result = integration_layer.process_request(analysis_type, project.path, user_message)
        
        # Salvar a análise
        analysis = Analysis(
            type=analysis_type,
            content=result,
            project_id=project.id
        )
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'id': analysis.id,
            'type': analysis.type,
            'content': analysis.content,
            'created_at': analysis.created_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao analisar projeto: {str(e)}")
        return jsonify({'error': f'Erro ao analisar projeto: {str(e)}'}), 500

@api.route('/api/analyses/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id):
    """Retorna uma análise específica"""
    analysis = Analysis.query.get_or_404(analysis_id)
    project = Project.query.get(analysis.project_id)
    
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': analysis.id,
        'type': analysis.type,
        'content': analysis.content,
        'created_at': analysis.created_at.isoformat(),
        'project_id': analysis.project_id
    })

@api.route('/api/projects/<int:project_id>/analyses', methods=['GET'])
@login_required
def get_project_analyses(project_id):
    """Retorna todas as análises de um projeto"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    analyses = Analysis.query.filter_by(project_id=project_id).order_by(Analysis.created_at.desc()).all()
    
    return jsonify([{
        'id': a.id,
        'type': a.type,
        'content': a.content,
        'created_at': a.created_at.isoformat()
    } for a in analyses])