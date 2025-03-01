# web_app/__init__.py

"""
Web application package for the Project Analyzer.
This package contains the Flask routes and static files.
"""

import os
import logging
from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS

def setup_logging():
    """Configure logging for the web application"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Add the console handler
    logger.addHandler(console_handler)
    
    return logger

def ensure_static_dir():
    """Ensure the static directory exists and is properly configured"""
    logger = setup_logging()
    
    try:
        # Get the absolute path to the static directory
        current_dir = Path(__file__).parent
        static_dir = current_dir / 'static'
        
        # Create static directory if it doesn't exist
        static_dir.mkdir(exist_ok=True)
        
        # Verify index.html exists
        index_path = static_dir / 'index.html'
        if index_path.exists():
            logger.info(f"index.html found at: {index_path}")
        else:
            logger.warning(f"index.html not found at: {index_path}")
        
        # Verify styles.css exists
        styles_path = static_dir / 'styles.css'
        if styles_path.exists():
            logger.info(f"styles.css found at: {styles_path}")
        else:
            logger.warning(f"styles.css not found at: {styles_path}")
        
        return str(static_dir)
        
    except Exception as e:
        logger.error(f"Error ensuring static directory: {str(e)}")
        raise

def create_app():
    """Create and configure the Flask application"""
    # Get static directory path
    static_dir = ensure_static_dir()
    
    # Initialize Flask app with static folder configuration
    app = Flask(__name__, 
                static_url_path='/static',
                static_folder=static_dir)
    
    # Enable CORS
    CORS(app)
    
    # Configure static file serving
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files"""
        return send_from_directory(static_dir, filename)
    
    # Configure root route
    @app.route('/')
    def serve_index():
        """Serve the index.html file"""
        return send_from_directory(static_dir, 'index.html')
    
    return app

# Initialize logging
logger = setup_logging()

# Initialize static directory
static_dir = ensure_static_dir()

# Log initialization
logger.info(f"Static directory ensured at: {static_dir}")

__all__ = ['create_app']
