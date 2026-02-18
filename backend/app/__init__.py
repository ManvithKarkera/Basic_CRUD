import logging
from flask import Flask
from flask_cors import CORS
from app.extensions import db
from app.routes import api
from app.error_handlers import register_error_handlers


def configure_logging():
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set specific log levels for different modules
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


def create_app(config=None):
    """
    Application factory pattern.
    Creates and configures the Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask application
    """
    # Configure logging first
    configure_logging()
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Override config if provided
    if config:
        app.config.update(config)
    
    # Enable CORS for frontend
    CORS(app, origins=["http://localhost:3000"])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints with /todos prefix
    app.register_blueprint(api, url_prefix='/todos')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    app.logger.info("Application started successfully")
    
    return app
