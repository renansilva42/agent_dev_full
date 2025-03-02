# web_app/routes.py
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from models.user import User
from models.project import Project
from models.analysis import Analysis
from database import db
from datetime import datetime

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    """Página inicial"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    return render_template('index.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Nome de usuário ou senha inválidos')
            return redirect(url_for('routes.login'))
        
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('routes.dashboard')
        return redirect(next_page)
    
    return render_template('login.html')

@routes.route('/logout')
@login_required
def logout():
    """Rota de logout"""
    logout_user()
    return redirect(url_for('routes.index'))

@routes.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe')
            return redirect(url_for('routes.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email já está em uso')
            return redirect(url_for('routes.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registro concluído com sucesso! Faça login para continuar.')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html')

@routes.route('/dashboard')
@login_required
def dashboard():
    """Rota do dashboard principal após login"""
    return render_template('dashboard.html')

@routes.route('/projects')
@login_required
def projects():
    """Lista projetos do usuário"""
    user_id = current_user.id
    projects = Project.query.filter_by(user_id=user_id).all()
    return render_template('projects.html', projects=projects)

@routes.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    """Detalhes de um projeto específico"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Você não tem permissão para acessar este projeto')
        return redirect(url_for('routes.projects'))
    
    analyses = Analysis.query.filter_by(project_id=project_id).order_by(Analysis.created_at.desc()).all()
    return render_template('project_detail.html', project=project, analyses=analyses)

@routes.route('/analyze/<int:project_id>')
@login_required
def analyze_project(project_id):
    """Página de análise de um projeto específico"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Você não tem permissão para acessar este projeto')
        return redirect(url_for('routes.projects'))
    
    return render_template('analyze.html', project=project)