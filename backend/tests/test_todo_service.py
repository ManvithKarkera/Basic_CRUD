"""
Unit tests for todo_service module.
Tests business logic, validation, and state transitions.
"""
import pytest
from app.services import todo_service
from app.services.todo_service import (
    STATUS_TODO,
    STATUS_IN_PROGRESS,
    STATUS_DONE
)
from app.exceptions import (
    ValidationError,
    NotFoundError,
    ConflictError
)
from app.models import Todo


class TestTodoCreation:
    """Tests for creating todo items."""
    
    def test_create_todo_with_valid_data(self, app, db):
        """Test creating a todo with valid title and description."""
        with app.app_context():
            todo = todo_service.create_todo("Buy groceries", "Milk, eggs, bread")
            
            assert todo is not None
            assert todo.sno is not None
            assert todo.title == "Buy groceries"
            assert todo.desc == "Milk, eggs, bread"
            assert todo.status == STATUS_TODO
            assert todo.date_created is not None
    
    def test_create_todo_with_default_status(self, app, db):
        """Test that newly created todos default to TODO status."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            
            assert todo.status == STATUS_TODO
    
    def test_create_todo_with_custom_status(self, app, db):
        """Test creating a todo with a specific initial status."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description", STATUS_IN_PROGRESS)
            
            assert todo.status == STATUS_IN_PROGRESS
    
    def test_create_todo_with_empty_title_fails(self, app, db):
        """Test that creating a todo with empty title raises ValidationError."""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                todo_service.create_todo("", "Description")
            
            assert "Title must not be empty or whitespace" in str(exc_info.value)
    
    def test_create_todo_with_whitespace_title_fails(self, app, db):
        """Test that creating a todo with whitespace-only title fails."""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                todo_service.create_todo("   ", "Description")
            
            assert "Title must not be empty or whitespace" in str(exc_info.value)
    
    def test_create_todo_trims_title_whitespace(self, app, db):
        """Test that title whitespace is trimmed during creation."""
        with app.app_context():
            todo = todo_service.create_todo("  Test task  ", "Description")
            
            assert todo.title == "Test task"
    
    def test_create_todo_with_invalid_status_fails(self, app, db):
        """Test that creating a todo with invalid status raises ValidationError."""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                todo_service.create_todo("Test task", "Description", "INVALID_STATUS")
            
            assert "Status must be one of" in str(exc_info.value)
    
    def test_database_remains_consistent_after_validation_failure(self, app, db):
        """Test that failed creation doesn't leave database in inconsistent state."""
        with app.app_context():
            # Try to create with empty title (should fail)
            with pytest.raises(ValidationError):
                todo_service.create_todo("", "Description")
            
            # Verify no todos were created
            todos = todo_service.get_all_todos()
            assert len(todos) == 0


class TestTodoRetrieval:
    """Tests for retrieving todo items."""
    
    def test_get_all_todos_empty_database(self, app, db):
        """Test getting all todos from empty database returns empty list."""
        with app.app_context():
            todos = todo_service.get_all_todos()
            
            assert todos == []
    
    def test_get_all_todos_returns_all_items(self, app, db):
        """Test that get_all_todos returns all created items."""
        with app.app_context():
            todo_service.create_todo("Task 1", "Description 1")
            todo_service.create_todo("Task 2", "Description 2")
            todo_service.create_todo("Task 3", "Description 3")
            
            todos = todo_service.get_all_todos()
            
            assert len(todos) == 3
    
    def test_get_todo_by_id_returns_correct_item(self, app, db):
        """Test retrieving a specific todo by ID."""
        with app.app_context():
            created_todo = todo_service.create_todo("Test task", "Description")
            
            retrieved_todo = todo_service.get_todo_by_id(created_todo.sno)
            
            assert retrieved_todo is not None
            assert retrieved_todo.sno == created_todo.sno
            assert retrieved_todo.title == created_todo.title
    
    def test_get_todo_by_id_nonexistent_returns_none(self, app, db):
        """Test that getting a non-existent todo returns None."""
        with app.app_context():
            todo = todo_service.get_todo_by_id(999)
            
            assert todo is None


class TestTodoUpdate:
    """Tests for updating todo items."""
    
    def test_update_todo_title_and_description(self, app, db):
        """Test updating a todo's title and description."""
        with app.app_context():
            todo = todo_service.create_todo("Original title", "Original desc")
            
            updated_todo = todo_service.update_todo(todo.sno, "New title", "New desc")
            
            assert updated_todo.title == "New title"
            assert updated_todo.desc == "New desc"
            assert updated_todo.status == STATUS_TODO  # Status unchanged
    
    def test_update_todo_trims_title_whitespace(self, app, db):
        """Test that whitespace is trimmed during update."""
        with app.app_context():
            todo = todo_service.create_todo("Original title", "Original desc")
            
            updated_todo = todo_service.update_todo(todo.sno, "  New title  ", "New desc")
            
            assert updated_todo.title == "New title"
    
    def test_update_todo_with_empty_title_fails(self, app, db):
        """Test that updating with empty title raises ValidationError."""
        with app.app_context():
            todo = todo_service.create_todo("Original title", "Original desc")
            
            with pytest.raises(ValidationError) as exc_info:
                todo_service.update_todo(todo.sno, "", "New desc")
            
            assert "Title must not be empty or whitespace" in str(exc_info.value)
    
    def test_update_nonexistent_todo_fails(self, app, db):
        """Test that updating a non-existent todo raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError) as exc_info:
                todo_service.update_todo(999, "New title", "New desc")
            
            assert "not found" in str(exc_info.value)
    
    def test_update_completed_todo_fails(self, app, db):
        """Test that updating a DONE todo raises ConflictError."""
        with app.app_context():
            # Create and transition to DONE
            todo = todo_service.create_todo("Test task", "Description")
            todo_service.update_todo_status(todo.sno, STATUS_IN_PROGRESS)
            todo_service.update_todo_status(todo.sno, STATUS_DONE)
            
            # Try to update
            with pytest.raises(ConflictError) as exc_info:
                todo_service.update_todo(todo.sno, "New title", "New desc")
            
            assert "Cannot modify a task that is already marked as DONE" in str(exc_info.value)
    
    def test_database_consistent_after_failed_update(self, app, db):
        """Test that database remains consistent after failed update."""
        with app.app_context():
            todo = todo_service.create_todo("Original title", "Original desc")
            original_title = todo.title
            
            # Try to update with empty title (should fail)
            with pytest.raises(ValidationError):
                todo_service.update_todo(todo.sno, "", "New desc")
            
            # Verify title wasn't changed
            retrieved_todo = todo_service.get_todo_by_id(todo.sno)
            assert retrieved_todo.title == original_title


class TestStatusTransitions:
    """Tests for status transitions and validation."""
    
    def test_valid_transition_todo_to_in_progress(self, app, db):
        """Test valid transition from TODO to IN_PROGRESS."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            
            updated_todo = todo_service.update_todo_status(todo.sno, STATUS_IN_PROGRESS)
            
            assert updated_todo.status == STATUS_IN_PROGRESS
    
    def test_valid_transition_in_progress_to_done(self, app, db):
        """Test valid transition from IN_PROGRESS to DONE."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            todo_service.update_todo_status(todo.sno, STATUS_IN_PROGRESS)
            
            updated_todo = todo_service.update_todo_status(todo.sno, STATUS_DONE)
            
            assert updated_todo.status == STATUS_DONE
    
    def test_invalid_transition_todo_to_done_fails(self, app, db):
        """Test that skipping from TODO to DONE raises ConflictError."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            
            with pytest.raises(ConflictError) as exc_info:
                todo_service.update_todo_status(todo.sno, STATUS_DONE)
            
            assert "Cannot transition from TODO to DONE" in str(exc_info.value)
    
    def test_transition_from_done_fails(self, app, db):
        """Test that transitioning from DONE to any state fails."""
        with app.app_context():
            # Create and transition to DONE
            todo = todo_service.create_todo("Test task", "Description")
            todo_service.update_todo_status(todo.sno, STATUS_IN_PROGRESS)
            todo_service.update_todo_status(todo.sno, STATUS_DONE)
            
            # Try to transition from DONE
            with pytest.raises(ConflictError) as exc_info:
                todo_service.update_todo_status(todo.sno, STATUS_TODO)
            
            assert "Cannot transition from DONE" in str(exc_info.value)
    
    def test_transition_to_same_status_is_noop(self, app, db):
        """Test that transitioning to same status is allowed (no-op)."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            
            updated_todo = todo_service.update_todo_status(todo.sno, STATUS_TODO)
            
            assert updated_todo.status == STATUS_TODO
    
    def test_invalid_status_value_fails(self, app, db):
        """Test that updating to invalid status value raises ValidationError."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            
            with pytest.raises(ValidationError) as exc_info:
                todo_service.update_todo_status(todo.sno, "INVALID_STATUS")
            
            assert "Status must be one of" in str(exc_info.value)
    
    def test_status_transition_on_nonexistent_todo_fails(self, app, db):
        """Test that status transition on non-existent todo raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                todo_service.update_todo_status(999, STATUS_IN_PROGRESS)
    
    def test_database_consistent_after_invalid_transition(self, app, db):
        """Test that database remains consistent after invalid transition attempt."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            original_status = todo.status
            
            # Try invalid transition (should fail)
            with pytest.raises(ConflictError):
                todo_service.update_todo_status(todo.sno, STATUS_DONE)
            
            # Verify status wasn't changed
            retrieved_todo = todo_service.get_todo_by_id(todo.sno)
            assert retrieved_todo.status == original_status


class TestTodoDeletion:
    """Tests for deleting todo items."""
    
    def test_delete_existing_todo(self, app, db):
        """Test deleting an existing todo."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            todo_id = todo.sno
            
            todo_service.delete_todo(todo_id)
            
            # Verify todo is deleted
            retrieved_todo = todo_service.get_todo_by_id(todo_id)
            assert retrieved_todo is None
    
    def test_delete_nonexistent_todo_fails(self, app, db):
        """Test that deleting a non-existent todo raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError) as exc_info:
                todo_service.delete_todo(999)
            
            assert "not found" in str(exc_info.value)
    
    def test_delete_does_not_affect_other_todos(self, app, db):
        """Test that deleting one todo doesn't affect others."""
        with app.app_context():
            todo1 = todo_service.create_todo("Task 1", "Description 1")
            todo2 = todo_service.create_todo("Task 2", "Description 2")
            todo3 = todo_service.create_todo("Task 3", "Description 3")
            
            todo_service.delete_todo(todo2.sno)
            
            # Verify other todos still exist
            assert todo_service.get_todo_by_id(todo1.sno) is not None
            assert todo_service.get_todo_by_id(todo3.sno) is not None
            assert todo_service.get_todo_by_id(todo2.sno) is None
    
    def test_can_delete_completed_todo(self, app, db):
        """Test that DONE todos can be deleted (deletion is always allowed)."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            todo_service.update_todo_status(todo.sno, STATUS_IN_PROGRESS)
            todo_service.update_todo_status(todo.sno, STATUS_DONE)
            
            # Should not raise any exception
            todo_service.delete_todo(todo.sno)
            
            assert todo_service.get_todo_by_id(todo.sno) is None


class TestComplexScenarios:
    """Tests for complex scenarios and edge cases."""
    
    def test_full_lifecycle_todo_to_done(self, app, db):
        """Test complete lifecycle: create -> in_progress -> done."""
        with app.app_context():
            # Create
            todo = todo_service.create_todo("Complete project", "Build and test")
            assert todo.status == STATUS_TODO
            
            # Start work
            todo = todo_service.update_todo_status(todo.sno, STATUS_IN_PROGRESS)
            assert todo.status == STATUS_IN_PROGRESS
            
            # Complete
            todo = todo_service.update_todo_status(todo.sno, STATUS_DONE)
            assert todo.status == STATUS_DONE
            
            # Verify cannot modify
            with pytest.raises(ConflictError):
                todo_service.update_todo(todo.sno, "New title", "New desc")
    
    def test_multiple_todos_with_different_statuses(self, app, db):
        """Test managing multiple todos with different statuses."""
        with app.app_context():
            todo1 = todo_service.create_todo("Task 1", "Description 1")
            todo2 = todo_service.create_todo("Task 2", "Description 2")
            todo3 = todo_service.create_todo("Task 3", "Description 3")
            
            # Different transitions
            todo_service.update_todo_status(todo1.sno, STATUS_IN_PROGRESS)
            todo_service.update_todo_status(todo2.sno, STATUS_IN_PROGRESS)
            todo_service.update_todo_status(todo2.sno, STATUS_DONE)
            
            # Verify states
            assert todo_service.get_todo_by_id(todo1.sno).status == STATUS_IN_PROGRESS
            assert todo_service.get_todo_by_id(todo2.sno).status == STATUS_DONE
            assert todo_service.get_todo_by_id(todo3.sno).status == STATUS_TODO
    
    def test_update_in_progress_todo_content(self, app, db):
        """Test that IN_PROGRESS todos can have their content updated."""
        with app.app_context():
            todo = todo_service.create_todo("Test task", "Description")
            todo_service.update_todo_status(todo.sno, STATUS_IN_PROGRESS)
            
            # Should succeed - only DONE is immutable
            updated_todo = todo_service.update_todo(todo.sno, "Updated title", "Updated desc")
            
            assert updated_todo.title == "Updated title"
            assert updated_todo.desc == "Updated desc"
            assert updated_todo.status == STATUS_IN_PROGRESS
