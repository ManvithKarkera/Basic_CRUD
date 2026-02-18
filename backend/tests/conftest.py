"""
Pytest configuration and fixtures for testing.
"""
import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope='function')
def app():
    """
    Create and configure a test Flask application instance.
    Uses SQLite in-memory database for testing.
    """
    test_config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TESTING': True
    }
    
    app = create_app(config=test_config)
    
    with app.app_context():
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """
    Provide a clean database for each test.
    """
    return _db


@pytest.fixture(scope='function')
def client(app):
    """
    Provide a test client for making HTTP requests.
    """
    return app.test_client()
