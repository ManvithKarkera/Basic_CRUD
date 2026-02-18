# Testing Guide

This document explains how to run the automated tests for the Flask Todo API.

## Setup

1. **Install test dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Verify pytest installation:**
   ```bash
   pytest --version
   ```

## Running Tests

### Run all tests:
```bash
cd backend
pytest
```

### Run with verbose output:
```bash
pytest -v
```

### Run with coverage report:
```bash
pytest --cov=app --cov-report=term-missing
```

### Run specific test file:
```bash
pytest tests/test_todo_service.py
```

### Run specific test class:
```bash
pytest tests/test_todo_service.py::TestTodoCreation
```

### Run specific test:
```bash
pytest tests/test_todo_service.py::TestTodoCreation::test_create_todo_with_valid_data
```

### Run tests matching a pattern:
```bash
pytest -k "status"  # Runs all tests with "status" in the name
```

## Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures and configuration
│   └── test_todo_service.py     # Service layer tests
├── pytest.ini                    # Pytest configuration
└── requirements.txt              # Includes pytest dependencies
```

## Test Coverage

The test suite covers:

### ✅ Todo Creation
- Valid task creation
- Creation with empty/whitespace title (validation)
- Creation with invalid status
- Title whitespace trimming
- Database consistency after failures

### ✅ Todo Retrieval
- Getting all todos
- Getting todo by ID
- Handling non-existent todos

### ✅ Todo Updates
- Updating title and description
- Validation of empty titles
- Prevention of updates to DONE tasks
- Database consistency after failures

### ✅ Status Transitions
- Valid transition: TODO → IN_PROGRESS
- Valid transition: IN_PROGRESS → DONE
- Invalid transition: TODO → DONE (blocked)
- Transitions from DONE (blocked)
- Invalid status values
- Database consistency after invalid transitions

### ✅ Todo Deletion
- Deleting existing todos
- Handling non-existent todos (404)
- Deletion doesn't affect other todos
- Deleting DONE todos (allowed)

### ✅ Complex Scenarios
- Full lifecycle workflows
- Multiple todos with different statuses
- Content updates for IN_PROGRESS todos

## Test Principles

1. **Isolated**: Each test runs with a fresh in-memory database
2. **Deterministic**: Tests produce consistent results
3. **Fast**: Uses SQLite in-memory database
4. **Readable**: Clear test names and single logical assertions
5. **Real DB**: No mocking of database layer

## Continuous Integration

To integrate with CI/CD pipelines:

```bash
# Run tests and generate XML report for CI
pytest --junitxml=test-results.xml

# Run with coverage and generate XML report
pytest --cov=app --cov-report=xml --cov-report=term
```

## Troubleshooting

### Tests fail with import errors
Ensure you're in the `backend` directory when running pytest:
```bash
cd backend
pytest
```

### Database-related errors
The tests use an in-memory SQLite database that's created fresh for each test. If you see database errors, ensure SQLAlchemy is properly installed:
```bash
pip install --upgrade Flask-SQLAlchemy
```

### Module not found errors
Make sure the backend directory structure is correct and all `__init__.py` files are present.
