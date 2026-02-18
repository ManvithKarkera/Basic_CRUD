"""
Centralized error handlers for Flask application.
Automatically converts exceptions to appropriate JSON responses.
"""
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException
from app.exceptions import APIException, ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Register all error handlers with the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """
        Handle all custom API exceptions.
        Automatically converts exception to JSON response with appropriate status code.
        """
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        
        logger.warning(
            f"API Exception: {error.__class__.__name__} - {error.message}",
            extra={
                'status_code': error.status_code,
                'error_type': error.__class__.__name__
            }
        )
        
        return response
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors (400)."""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        
        logger.warning(
            f"Validation Error: {error.message}",
            extra={'status_code': 400}
        )
        
        return response
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        """Handle not found errors (404)."""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        
        logger.info(
            f"Not Found: {error.message}",
            extra={'status_code': 404}
        )
        
        return response
    
    @app.errorhandler(ConflictError)
    def handle_conflict_error(error):
        """Handle conflict errors (409)."""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        
        logger.warning(
            f"Conflict Error: {error.message}",
            extra={'status_code': 409}
        )
        
        return response
    
    @app.errorhandler(404)
    def handle_404(error):
        """Handle Flask's built-in 404 errors (route not found)."""
        logger.info(f"Route not found: {error}")
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def handle_500(error):
        """Handle internal server errors."""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle other HTTP exceptions from Werkzeug."""
        logger.warning(f"HTTP Exception: {error.code} - {error.description}")
        return jsonify({'error': error.description}), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """
        Catch-all handler for unexpected errors.
        Logs the full exception and returns a safe error message.
        """
        logger.error(
            f"Unexpected error: {error.__class__.__name__} - {str(error)}",
            exc_info=True,
            extra={'error_type': error.__class__.__name__}
        )
        return jsonify({'error': 'An unexpected error occurred'}), 500
