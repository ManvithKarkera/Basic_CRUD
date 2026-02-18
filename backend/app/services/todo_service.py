import logging
from typing import List, Optional, Dict
from app.extensions import db
from app.models import Todo
from app.exceptions import ValidationError, NotFoundError, ConflictError

# Configure logging
logger = logging.getLogger(__name__)

# Status constants
STATUS_TODO = 'TODO'
STATUS_IN_PROGRESS = 'IN_PROGRESS'
STATUS_DONE = 'DONE'

VALID_STATUSES = [STATUS_TODO, STATUS_IN_PROGRESS, STATUS_DONE]

# Allowed status transitions
ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    STATUS_TODO: [STATUS_IN_PROGRESS],
    STATUS_IN_PROGRESS: [STATUS_DONE],
    STATUS_DONE: []  # DONE is final, no transitions allowed
}


# Validation Functions
def validate_title(title: str) -> None:
    """
    Validate that title is not empty or whitespace.
    
    Args:
        title: The title to validate
        
    Raises:
        ValidationError: If title is invalid
    """
    if not title or not title.strip():
        logger.warning("Validation failed: Title is empty or whitespace")
        raise ValidationError("Title must not be empty or whitespace")


def validate_status(status: str) -> None:
    """
    Validate that status is one of the allowed values.
    
    Args:
        status: The status to validate
        
    Raises:
        ValidationError: If status is invalid
    """
    if status not in VALID_STATUSES:
        logger.warning(f"Validation failed: Invalid status '{status}'. Allowed: {VALID_STATUSES}")
        raise ValidationError(f"Status must be one of: {', '.join(VALID_STATUSES)}")


def validate_status_transition(current_status: str, new_status: str) -> None:
    """
    Validate that a status transition is allowed.
    
    Args:
        current_status: The current status
        new_status: The desired new status
        
    Raises:
        ConflictError: If transition is not allowed
    """
    if new_status == current_status:
        return  # Same status is allowed (no-op)
    
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        logger.warning(
            f"Invalid status transition attempted",
            extra={
                'operation': 'status_transition',
                'current_status': current_status,
                'attempted_status': new_status,
                'allowed_transitions': allowed
            }
        )
        raise ConflictError(
            f"Cannot transition from {current_status} to {new_status}. "
            f"Allowed transitions: {' -> '.join(allowed) if allowed else 'none (final state)'}"
        )


def check_task_not_completed(todo: Todo) -> None:
    """
    Check that a task is not in DONE status.
    
    Args:
        todo: The todo item to check
        
    Raises:
        ConflictError: If task is already completed
    """
    if todo.status == STATUS_DONE:
        logger.warning(
            f"Attempt to modify completed task",
            extra={
                'operation': 'modify_completed_task',
                'todo_id': todo.sno,
                'status': STATUS_DONE
            }
        )
        raise ConflictError("Cannot modify a task that is already marked as DONE")


# CRUD Functions
def get_all_todos() -> List[Todo]:
    """
    Retrieve all todo items from the database.
    
    Returns:
        List of all Todo objects
    """
    return Todo.query.all()  # type: ignore


def create_todo(title: str, desc: str, status: str = STATUS_TODO) -> Todo:
    """
    Create a new todo item with validation.
    
    Args:
        title: The title of the todo
        desc: The description of the todo
        status: The initial status (defaults to TODO)
        
    Returns:
        The newly created Todo object
        
    Raises:
        ValidationError: If input validation fails
    """
    # Validate inputs
    validate_title(title)
    validate_status(status)
    
    # Create todo
    todo = Todo(title=title.strip(), desc=desc, status=status)  # type: ignore
    db.session.add(todo)
    db.session.commit()
    
    logger.info(
        f"Created new todo",
        extra={
            'operation': 'create_todo',
            'todo_id': todo.sno,
            'status': status,
            'title': title.strip()
        }
    )
    return todo


def get_todo_by_id(sno: int) -> Optional[Todo]:
    """
    Retrieve a specific todo item by its ID.
    
    Args:
        sno: The ID of the todo item
        
    Returns:
        The Todo object if found, None otherwise
    """
    return Todo.query.filter_by(sno=sno).first()  # type: ignore


def delete_todo(sno: int) -> None:
    """
    Delete a todo item by its ID.
    
    Args:
        sno: The ID of the todo item to delete
        
    Raises:
        NotFoundError: If the todo item is not found
    """
    todo = get_todo_by_id(sno)
    if not todo:
        logger.info(
            f"Attempted to delete non-existent todo",
            extra={
                'operation': 'delete_todo',
                'todo_id': sno
            }
        )
        raise NotFoundError(f"Todo with id {sno} not found")
    
    db.session.delete(todo)  # type: ignore
    db.session.commit()
    
    logger.info(
        f"Deleted todo",
        extra={
            'operation': 'delete_todo',
            'todo_id': sno
        }
    )


def update_todo(sno: int, title: str, desc: str) -> Todo:
    """
    Update an existing todo item's title and description.
    
    Args:
        sno: The ID of the todo item to update
        title: The new title
        desc: The new description
        
    Returns:
        The updated Todo object
        
    Raises:
        NotFoundError: If the todo item is not found
        ValidationError: If input validation fails
        ConflictError: If task is already completed
    """
    todo = get_todo_by_id(sno)
    if not todo:
        logger.info(
            f"Attempted to update non-existent todo",
            extra={
                'operation': 'update_todo',
                'todo_id': sno
            }
        )
        raise NotFoundError(f"Todo with id {sno} not found")
    
    # Check if task is completed
    check_task_not_completed(todo)
    
    # Validate new title
    validate_title(title)
    
    # Update fields
    old_title = todo.title
    todo.title = title.strip()
    todo.desc = desc
    db.session.add(todo)  # type: ignore
    db.session.commit()
    
    logger.info(
        f"Updated todo",
        extra={
            'operation': 'update_todo',
            'todo_id': sno,
            'old_title': old_title,
            'new_title': title.strip()
        }
    )
    return todo


def update_todo_status(sno: int, new_status: str) -> Todo:
    """
    Update the status of a todo item with transition validation.
    
    Args:
        sno: The ID of the todo item to update
        new_status: The new status
        
    Returns:
        The updated Todo object
        
    Raises:
        NotFoundError: If the todo item is not found
        ValidationError: If status is invalid
        ConflictError: If status transition is not allowed
    """
    todo = get_todo_by_id(sno)
    if not todo:
        logger.info(
            f"Attempted to update status of non-existent todo",
            extra={
                'operation': 'update_todo_status',
                'todo_id': sno
            }
        )
        raise NotFoundError(f"Todo with id {sno} not found")
    
    # Validate status value
    validate_status(new_status)
    
    # Validate status transition
    validate_status_transition(todo.status, new_status)
    
    # Update status
    old_status = todo.status
    todo.status = new_status
    db.session.add(todo)  # type: ignore
    db.session.commit()
    
    logger.info(
        f"Status transition successful",
        extra={
            'operation': 'status_transition',
            'todo_id': sno,
            'old_status': old_status,
            'new_status': new_status
        }
    )
    return todo
