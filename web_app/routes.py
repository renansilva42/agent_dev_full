# web_app/routes.py

from flask import request, jsonify, session, current_app, send_from_directory
from integration.integration_layer import IntegrationError
import os
import logging
from pathlib import Path

def configure_routes(app, integration_layer):
    """Configure routes for the Flask application"""
    
    logger = logging.getLogger(__name__)
    
    # Serve static files
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files"""
        try:
            static_dir = os.path.join(current_app.root_path, 'web_app', 'static')
            logger.info(f"Serving static file: {filename} from {static_dir}")
            return send_from_directory(static_dir, filename)
        except Exception as e:
            logger.error(f"Error serving static file {filename}: {str(e)}")
            return {'error': str(e)}, 500
    
    @app.route('/')
    def index():
        """Serve the index.html file"""
        try:
            static_dir = os.path.join(current_app.root_path, 'web_app', 'static')
            logger.info(f"Serving index.html from {static_dir}")
            return send_from_directory(static_dir, 'index.html')
        except Exception as e:
            logger.error(f"Error serving index.html: {str(e)}")
            return {'error': str(e)}, 500
    
    @app.route('/set_project_path', methods=['POST'])
    def set_project_path():
        """Set the project path in the session"""
        try:
            if not request.is_json:
                return jsonify({'success': False, 'message': 'Request must be JSON'}), 400
                
            project_path = request.json.get('project_path')
            if not project_path:
                return jsonify({'success': False, 'message': 'Project path is required'}), 400
            
            # Log the received path
            logger.info(f"Received project path: {project_path}")
            
            # Convert to Path object for better path handling
            path = Path(project_path)
            
            # Log the initial path object
            logger.info(f"Initial path object: {path}")
            
            # Common locations to search
            search_paths = [
                Path.home() / 'Desktop',
                Path.home() / 'Documents',
                Path.home() / 'Downloads',
                Path.cwd(),
                Path('/Users/renansilva/VS Code Workspace'),
                Path('/Users/renansilva/VS Code Workspace/agent_dev_full')
            ]
            
            # Log search paths
            logger.info(f"Searching in paths: {search_paths}")
            
            found_path = None
            
            # Try to find the folder
            for search_path in search_paths:
                try:
                    # Look for exact match
                    potential_path = search_path / path.name
                    logger.info(f"Checking path: {potential_path}")
                    
                    if potential_path.is_dir():
                        found_path = potential_path
                        logger.info(f"Found exact match: {found_path}")
                        break
                        
                    # Look for case-insensitive match
                    for item in search_path.iterdir():
                        if item.is_dir() and item.name.lower() == path.name.lower():
                            found_path = item
                            logger.info(f"Found case-insensitive match: {found_path}")
                            break
                            
                except Exception as e:
                    logger.warning(f"Error searching in {search_path}: {e}")
                    continue
            
            if found_path:
                project_path = str(found_path.resolve())
            else:
                # If not found in common locations, try the original path
                original_path = Path(project_path).resolve()
                if original_path.is_dir():
                    project_path = str(original_path)
                    logger.info(f"Using original path: {project_path}")
                else:
                    logger.error(f"Directory not found: {project_path}")
                    return jsonify({
                        'success': False,
                        'message': f'Directory not found: {project_path}'
                    }), 400
            
            # Log the final resolved path
            logger.info(f"Final resolved path: {project_path}")
            
            # Check if the directory is readable
            try:
                files = list(Path(project_path).iterdir())
                logger.info(f"Found {len(files)} items in directory")
            except PermissionError:
                logger.error(f"Permission denied: {project_path}")
                return jsonify({
                    'success': False,
                    'message': f'Cannot access directory: {project_path}'
                }), 400
            except Exception as e:
                logger.error(f"Error accessing directory: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error accessing directory: {str(e)}'
                }), 400
            
            # Store the normalized path
            session['project_path'] = project_path
            
            # Log the successful path setting
            logger.info(f"Project path set to: {project_path}")
            
            return jsonify({
                'success': True,
                'message': 'Project path set successfully',
                'path': project_path
            })
                
        except Exception as e:
            logger.error(f"Error setting project path: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error setting project path: {str(e)}'
            }), 500
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """Handle chat messages and return responses"""
        try:
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
                
            user_message = request.json.get('message')
            if not user_message:
                return jsonify({'error': 'Message is required'}), 400
                
            project_path = session.get('project_path')
            if not project_path:
                return jsonify({'response': 'Please set a project path first'})
            
            # Verify the project path still exists and is accessible
            if not Path(project_path).is_dir():
                session.pop('project_path', None)
                return jsonify({'response': 'Project directory no longer exists. Please select a new path.'})
            
            try:
                # Process request with all agents and optimize response
                response = integration_layer.process_request(
                    'general',  # Using general type to trigger request analyzer
                    project_path,
                    user_message
                )
                return jsonify({'response': response})
                
            except IntegrationError as e:
                logger.error(f"Integration error: {str(e)}")
                return jsonify({'response': f'Error: {str(e)}'})
                
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return jsonify({
                'response': f'Error: {str(e)}'
            })
