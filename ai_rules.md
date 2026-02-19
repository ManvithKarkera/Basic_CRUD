# AI-Assisted Development Rules

## Purpose

This document defines constraints and guidelines for using AI tools when developing this Flask API project. These rules ensure code quality, maintainability, and safety while leveraging AI assistance effectively.

## Architectural Boundaries

### Three-Layer Architecture

1. **Models Layer** (`app/models.py`)
   - Database schema definitions only
   - ORM model classes
   - Serialization methods (`to_dict()`)
   - No business logic
   - No database queries

2. **Services Layer** (`app/services/`)
   - All business logic
   - All database queries
   - Validation functions
   - State management
   - Domain rules enforcement

3. **Routes Layer** (`app/routes.py`)
   - HTTP request/response handling
   - Input parsing and validation
   - Response formatting
   - Delegates to services
   - No business logic
   - No database access

### RULE: Strict Layer Separation

**FORBIDDEN**:
- Business logic in route handlers
- Database queries in route handlers
- Business logic in models
- Routes calling database directly

**REQUIRED**:
- All database operations through service layer
- All business rules in service layer
- Routes call services, services call database

## Code Quality Requirements

### RULE: Input Validation

**REQUIRED**:
- Validate all user inputs before processing
- Reject invalid data with clear error messages
- Use type checking for function parameters
- Validate data types, ranges, and constraints

**Example**:
```python
# CORRECT
def validate_title(title):
    if not title or not isinstance(title, str):
        raise ValidationError("Title must be a non-empty string")
    if len(title.strip()) == 0:
        raise ValidationError("Title cannot be blank")
    return title.strip()

# INCORRECT - No validation
def create_todo(title):
    todo = Todo(title=title)  # Accepting any input
```

### RULE: No Direct Database Access

**FORBIDDEN**:
```python
# In routes.py - WRONG
@bp.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()  # Direct DB access
    return jsonify([t.to_dict() for t in todos])
```

**REQUIRED**:
```python
# In routes.py - CORRECT
@bp.route('/todos', methods=['GET'])
def get_todos():
    todos = todo_service.get_all_todos()  # Service layer
    return jsonify([t.to_dict() for t in todos])
```

### RULE: Testing for Business Rules

**REQUIRED**:
- Every new business rule must have corresponding tests
- Test both valid and invalid cases
- Test boundary conditions
- Verify database state after operations

**Example**:
```python
# If you add this business rule:
def validate_status_transition(current, new):
    if current == 'DONE':
        raise ConflictError("Cannot modify completed task")

# You MUST add tests:
def test_cannot_modify_completed_task():
    # Test code here
```

### RULE: Explicit Error Handling

**REQUIRED**:
- Use custom exceptions for domain errors
- Map exceptions to HTTP status codes
- Provide clear, actionable error messages
- Log all errors with context

**FORBIDDEN**:
- Generic exceptions like `Exception` or `RuntimeError`
- Empty except blocks
- Swallowing errors without logging

### RULE: Structured Logging

**REQUIRED** for:
- Entity creation/deletion
- State transitions
- Validation failures
- Business rule violations

**Format**:
```python
logging.info(
    "Operation description",
    extra={
        'operation': 'operation_name',
        'entity_id': entity_id,
        'additional_context': value
    }
)
```

**FORBIDDEN**:
- Logging sensitive data (passwords, tokens)
- Logging full request bodies
- Debug logging in production code paths

### RULE: Test Before Implementation

**PROCESS**:
1. Write failing test for new feature
2. Ask AI to implement feature
3. Verify test now passes
4. Add additional edge case tests

**FORBIDDEN**:
- Implementing features without tests
- Writing tests after implementation
- Skipping tests for "simple" features

### RULE: Impact Evaluation

**REQUIRED** before modifying services:
- List all functions that call modified function
- Check all route handlers that use the service
- Review tests that might be affected
- Search codebase for usage patterns

**QUESTIONS** to answer:
- What breaks if this change is wrong?
- Which tests need updating?
- Are there cascading changes required?
- What are the backward compatibility implications?

## Coding Standards

### File Organization

```
backend/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models only
│   ├── routes.py            # HTTP handlers only
│   ├── extensions.py        # Shared extensions (db, etc.)
│   ├── exceptions.py        # Custom exceptions
│   ├── error_handlers.py    # Flask error handlers
│   └── services/
│       └── todo_service.py  # Business logic
└── tests/
    └── test_*.py            # Test modules
```

### Naming Conventions

**Functions**:
- Services: `verb_noun` (e.g., `create_todo`, `validate_status`)
- Routes: REST resource names (e.g., `create_todo`, `update_todo`)
- Tests: `test_description_of_behavior` (e.g., `test_invalid_transition_fails`)

**Exceptions**:
- Descriptive names ending in `Error` (e.g., `ValidationError`, `NotFoundError`)

**Variables**:
- Descriptive, no abbreviations unless standard (e.g., `todo`, not `td`)

### Function Size

**GUIDELINES**:
- Functions should do one thing
- Maximum ~30 lines for service functions
- Maximum ~15 lines for route handlers
- Extract complex logic into helper functions

### Documentation

**REQUIRED**:
- Docstrings for public service functions
- Comments for non-obvious business rules
- Documentation of state transitions

**NOT REQUIRED**:
- Comments for obvious code
- Paraphrasing code in comments

## Security Requirements

### RULE: No Security Shortcuts

**REQUIRED**:
- Sanitize all user inputs
- Use parameterized queries (SQLAlchemy ORM does this)
- Validate data types and ranges
- Return generic error messages to users

**FORBIDDEN**:
- Trusting user input
- Exposing stack traces to users
- Logging sensitive information
- SQL string concatenation

### RULE: Fail Safely

**REQUIRED**:
- Default to denying operations
- Return 400/404/409 for client errors
- Return 500 for server errors
- Rollback database on errors

**Example**:
```python
# CORRECT - Explicit allow list
VALID_STATUSES = ['TODO', 'IN_PROGRESS', 'DONE']
if status not in VALID_STATUSES:
    raise ValidationError(f"Invalid status: {status}")

# INCORRECT - Implicit trust
if status == 'INVALID':
    raise ValidationError("Invalid status")
# What if status is something unexpected?
```

## Summary

These rules formalize best practices for AI-assisted development on this Flask API project. They prioritize:

1. **Safety**: Validation, error handling, security
2. **Maintainability**: Clear structure, separation of concerns
3. **Quality**: Testing, review, simplicity
4. **Reliability**: Logging, fail-safe defaults

All AI-generated code must comply with these rules. When in doubt, prefer simplicity and explicitness over cleverness.

---

