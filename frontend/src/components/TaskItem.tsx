import React, { useState } from 'react';
import { Task, TaskStatus, getAvailableTransitions, canTransitionTo } from '../types/Task';
import { todoApi } from '../api/todoApi';

interface TaskItemProps {
  task: Task;
  onTaskUpdated: () => void;
  onTaskDeleted: () => void;
}

export const TaskItem: React.FC<TaskItemProps> = ({ task, onTaskUpdated, onTaskDeleted }) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const availableTransitions = getAvailableTransitions(task.status);
  const isTerminalState = availableTransitions.length === 0;

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (!canTransitionTo(task.status, newStatus)) {
      setError(`Cannot transition from ${task.status} to ${newStatus}`);
      return;
    }

    setIsUpdating(true);
    setError(null);

    try {
      await todoApi.updateTodo(task.id, { status: newStatus });
      onTaskUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Delete task "${task.title}"?`)) {
      return;
    }

    setIsDeleting(true);
    setError(null);

    try {
      await todoApi.deleteTodo(task.id);
      onTaskDeleted();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      setIsDeleting(false);
    }
  };

  return (
    <div className={`task-item status-${task.status.toLowerCase()}`}>
      <div className="task-header">
        <h3>{task.title}</h3>
        <span className={`status-badge ${task.status.toLowerCase()}`}>
          {task.status}
        </span>
      </div>

      <div className="task-meta">
        <small>Created: {new Date(task.date_created).toLocaleString()}</small>
      </div>

      {!isTerminalState && (
        <div className="task-actions">
          <label>Transition to:</label>
          {availableTransitions.map((status) => (
            <button
              key={status}
              onClick={() => handleStatusChange(status)}
              disabled={isUpdating || isDeleting}
              className="transition-button"
            >
              {status}
            </button>
          ))}
        </div>
      )}

      {isTerminalState && (
        <div className="task-info">
          <small>Task completed (cannot be modified)</small>
        </div>
      )}

      <button
        onClick={handleDelete}
        disabled={isDeleting || isUpdating}
        className="delete-button"
      >
        {isDeleting ? 'Deleting...' : 'Delete'}
      </button>

      {error && <div className="error">{error}</div>}
    </div>
  );
};
