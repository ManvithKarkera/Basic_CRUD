# Flask Task Management API

## Overview

A JSON REST API for managing tasks with status transitions. Built to demonstrate clean architecture, domain rule enforcement, and verification through testing.

### Design Philosophy

- **Small, well-defined boundaries**: Models, services, and routes have distinct responsibilities
- **Invalid states prevented at compile and runtime**: Type validation and state machine enforcement
- **Change resilience**: Service layer isolates business rules from HTTP concerns
- **Simplicity over abstraction**: Direct implementations, no unnecessary frameworks

## Architecture

### Folder Structure

```
backend/
├── app/
│   ├── __init__.py          # Application factory, logging configuration
│   ├── models.py            # Database schema only
│   ├── routes.py            # HTTP request/response handling
│   ├── extensions.py        # SQLAlchemy instance
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── error_handlers.py    # Centralized error handling
│   └── services/
│       └── todo_service.py  # Business logic and validation
├── tests/
│   ├── conftest.py          # Test fixtures and configuration
│   └── test_todo_service.py # Service layer tests
└── instance/
    └── todos.db             # SQLite database (generated)
```

### Layer Responsibilities

**Models** (`models.py`):
- Database schema definitions
- ORM relationships
- Data serialization (`to_dict()`)
- **No business logic or queries**

**Services** (`services/todo_service.py`):
- All business logic
- All database queries
- Validation functions
- State transition enforcement
- Domain rule implementations

**Routes** (`routes.py`):
- HTTP request parsing
- Input validation
- Service delegation
- Response formatting
- **No business logic or database access**

### Why This Separation

**Problem**: In monolithic route handlers, business rules are scattered, database logic is duplicated, and changes cascade unpredictably.

**Solution**: Service layer acts as a stable interface. Routes can change HTTP details (status codes, response format) without touching business logic. Business rules can evolve without modifying HTTP handling.

**Result**: Changes are isolated, tests are focused, and modifications are safer.

## Domain Rules & Invariants

### Status State Machine

```
TODO → IN_PROGRESS → DONE
```

**Rules**:
1. New tasks start as `TODO`
2. Valid transitions: `TODO → IN_PROGRESS`, `IN_PROGRESS → DONE`, `TODO → DONE`
3. `DONE` is terminal: completed tasks cannot be modified
4. Only valid status values accepted: `TODO`, `IN_PROGRESS`, `DONE`

### Validation Logic

**Title Validation**:
- Must be non-empty string
- Cannot be blank (only whitespace)
- Automatically strips whitespace

**Status Validation**:
- Must be one of three valid values
- State transitions checked against current state
- Invalid transitions rejected with `409 Conflict`

### Why These Rules

**Prevents**:
- Tasks stuck in inconsistent states
- Accidental modification of completed work
- Invalid status values in database
- Race conditions from status changes

**Enforces**:
- Clear lifecycle progression
- Audit trail of state changes
- Predictable system behavior

## Interface Safety

### Validation Strategy

**Defense in depth**:
1. Type checking at service layer
2. Value validation before database operations
3. State verification before transitions
4. Database constraints as final safety net

**All inputs validated** before processing. Invalid data rejected immediately with clear error messages.

### HTTP Status Codes

- `200 OK`: Successful GET/PUT
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid input (ValidationError)
- `404 Not Found`: Resource doesn't exist (NotFoundError)
- `409 Conflict`: Invalid state transition (ConflictError)
- `500 Internal Server Error`: Unexpected server issues

### Error Handling Strategy

**Custom Exception Hierarchy**:
```python
APIException (base)
├── ValidationError (400)
├── NotFoundError (404)
└── ConflictError (409)
```

**Centralized Error Handlers**:
- Convert exceptions to JSON automatically
- Map exception types to HTTP status codes
- Log all errors with structured context
- Never expose stack traces to clients

**Benefits**:
- Services raise domain exceptions, not HTTP errors
- Error handling logic is not duplicated
- Consistent error response format
- Changes to error handling in one place

## Verification Strategy

### What Is Tested

**Service Layer** (`test_todo_service.py`):
- CRUD operations: create, read, update, delete
- Validation: title and status validation
- State transitions: valid and invalid transitions
- Edge cases: nonexistent todos, completed task modifications
- Database consistency: state verification after operations

**45+ Tests** organized by concern:
- `TestTodoCreation`: Creation and initial state
- `TestTodoRetrieval`: Fetching todos
- `TestTodoUpdate`: Basic updates
- `TestStatusValidation`: Status field validation
- `TestStatusTransitions`: State machine enforcement
- `TestTodoDeletion`: Deletion operations
- `TestComplexScenarios`: Full lifecycle workflows

### Why Services Are Tested Directly

**Rationale**:
- Business logic lives in services, not routes
- Routes are thin delegators (minimal logic to test)
- Service tests verify domain rules independently of HTTP
- Faster test execution (no HTTP overhead)
- Clearer test failures (direct function calls)

**Route testing** would mostly verify Flask's routing, not our business logic.

### How Tests Protect Future Changes

1. **Prevent regressions**: All 45+ tests must pass before merging
2. **Document behavior**: Tests are executable specifications
3. **Enable refactoring**: Change implementation confidently if tests pass
4. **Catch invariant violations**: Tests verify database consistency

**Example**: If status transition logic is refactored, tests immediately catch broken state machine rules.

## Observability

### Logging Strategy

**Structured logging** with operation context:
```python
logging.info(
    "Todo created successfully",
    extra={'operation': 'create_todo', 'todo_id': todo.id}
)
```

**What is logged**:
- Entity creation and deletion
- Status transitions
- Validation failures
- All exceptions (with context)

**What is NOT logged**:
- Sensitive data
- Full request bodies
- User identifiers (in this demo project)

### Centralized Error Handling

**Flask error handlers** (`error_handlers.py`):
- Catch all `APIException` subclasses
- Convert to JSON responses automatically
- Log errors with structured context
- Map exception types to status codes

**Benefits**:
- Services don't handle HTTP concerns
- Error logging is consistent
- Error responses are uniform
- Easy to modify error behavior globally

## AI Usage Strategy

### How AI Was Used

**Code Generation**:
- Application factory boilerplate
- Service function implementations
- Test case generation (~45 tests)
- Exception class definitions
- Logging configuration

**Refactoring**:
- Converting HTML templates to JSON responses
- Extracting service layer from routes
- Centralizing error handling
- Implementing state transition logic

**Time Saved**: Estimated 40-60 hours across 6 development phases

### How Output Was Reviewed

**Every AI-generated code block reviewed for**:
1. **Correctness**: Logic matches requirements
2. **Security**: No SQL injection, proper validation
3. **Maintainability**: Clear, simple implementations
4. **Standards**: Follows project conventions
5. **Edge cases**: Handles invalid inputs

**Verification process**:
- Manual code review (line-by-line for critical sections)
- Full test suite execution
- Manual endpoint testing
- Log output inspection
- Database state verification

### How Architectural Integrity Was Enforced

**Rules enforced during AI assistance**:
- Business logic only in services
- No database access in routes
- All inputs validated
- Tests required for business rules
- Simple implementations preferred

**AI suggestions rejected when**:
- They violated layer separation
- They added unnecessary abstraction
- They skipped validation
- They were too clever/complex

**Documentation**: See `ai_rules.md` for complete guidelines

## Tradeoffs & Limitations

### What Was Intentionally Not Built

**Authentication/Authorization**: Not included to focus on architecture and domain rules. Would add JWT tokens or session management before production.

**Pagination**: Not implemented for todo list endpoint. Current assumption: small todo lists. Would add `limit`/`offset` parameters for larger datasets.

**Database Migrations**: Using SQLAlchemy's `db.create_all()` for simplicity. Would use Alembic for production schema evolution.

**Async Operations**: Synchronous Flask app. Task counts assumed small. Would consider async (e.g., FastAPI) if handling high concurrency or I/O-bound operations.

**Soft Deletes**: Todos are hard-deleted. Would add `deleted_at` timestamp for audit requirements.

### Why Complexity Was Avoided

**Principle**: Add complexity only when required by real requirements.

**Examples**:
- No repository pattern (SQLAlchemy already abstracts database)
- No dependency injection framework (Python functions work fine)
- No event system (direct function calls are clear)
- No API versioning (single version, breaking changes acceptable during development)

**Result**: 
- Codebase remains small (~600 lines)
- Easy to understand in one reading
- Fast test execution
- Simple to modify

### Future Extension Strategy

**To add authentication**:
1. Add User model
2. Implement login/token generation route
3. Add authentication decorator
4. Associate todos with users
5. Filter queries by current user

**To add task priorities**:
1. Add priority field to model
2. Add validation in service layer
3. Add tests for priority handling
4. Update routes to accept priority parameter

**To add task dependencies**:
1. Add parent_id foreign key
2. Add validation preventing dependency cycles
3. Add tests for dependency rules
4. Update deletion logic for cascades

**Architecture supports extensions**: New domain rules live in services, new fields in models, new endpoints in routes. Layers remain separate.

## How to Run

### Prerequisites

- Python 3.10+
- pip

### Setup

1. **Clone repository and navigate to project folder**:
   ```powershell
   cd flask
   ```

2. **Create virtual environment**:
   ```powershell
   python -m venv env
   ```

3. **Activate virtual environment**:
   ```powershell
   .\env\Scripts\activate
   ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Run Development Server

```powershell
cd backend
$env:FLASK_APP="app"
$env:FLASK_ENV="development"
flask run
```

Server runs at `http://127.0.0.1:5000`

### Run Tests

```powershell
cd backend
python -m pytest tests/ -v
```

**Run with coverage**:
```powershell
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/todos` | List all todos |
| POST | `/todos` | Create new todo |
| GET | `/todos/<id>` | Get specific todo |
| PUT | `/todos/<id>` | Update todo |
| DELETE | `/todos/<id>` | Delete todo |

**Example: Create todo**:
```bash
curl -X POST http://127.0.0.1:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Flask", "status": "TODO"}'
```

**Example: Update status**:
```bash
curl -X PUT http://127.0.0.1:5000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS"}'
```

## Project Context

**Purpose**: Engineering assessment demonstrating architectural discipline, domain modeling, and verification practices.

**Focus Areas**:
- Clean separation of concerns
- Business rule enforcement
- Invalid state prevention
- Test coverage
- AI-assisted development with review

**Not a production system**: Authentication, authorization, rate limiting, input sanitization, and production deployment concerns deliberately excluded to focus on core architecture.

---

**Last Updated**: February 19, 2026
