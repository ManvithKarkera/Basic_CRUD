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
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDesc, setEditDesc] = useState(task.desc || '');
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

  const handleEdit = async () => {
    if (!editTitle.trim()) {
      setError('Title cannot be empty');
      return;
    }

    setIsUpdating(true);
    setError(null);

    try {
      await todoApi.updateTodo(task.id, { title: editTitle.trim(), desc: editDesc.trim() });
      setIsEditing(false);
      onTaskUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setEditDesc(task.desc || '');
    setIsEditing(false);
    setError(null);
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
      {isEditing ? (
        <div className="task-edit">
          <div className="form-group">
            <label>Title:</label>
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              disabled={isUpdating}
            />
          </div>
          <div className="form-group">
            <label>Description:</label>
            <textarea
              value={editDesc}
              onChange={(e) => setEditDesc(e.target.value)}
              disabled={isUpdating}
              rows={3}
            />
          </div>
          <div className="edit-actions">
            <button onClick={handleEdit} disabled={isUpdating} className="save-button">
              {isUpdating ? 'Saving...' : 'Save'}
            </button>
            <button onClick={handleCancelEdit} disabled={isUpdating} className="cancel-button">
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="task-header">
            <h3>{task.title}</h3>
            <span className={`status-badge ${task.status.toLowerCase()}`}>
              {task.status}
            </span>
          </div>

          {task.desc && (
            <div className="task-description">
              <p>{task.desc}</p>
            </div>
          )}

          <div className="task-meta">
            <small>Created: {new Date(task.date_created).toLocaleString()}</small>
          </div>
        </>
      )}

      {!isEditing && (
        <>
          {!isTerminalState && (
            <div className="task-actions">
              <label>Transition to:</label>
              {availableTransitions.map((status) => (
                <button
                  key={status}
                  onClick={() => handleStatusChange(status)}
                  disabled={isUpdating || isDeleting}
                  className={`transition-button transition-${status.toLowerCase()}`}
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

          <div className="action-buttons">
            {!isTerminalState && (
              <button
                onClick={() => setIsEditing(true)}
                disabled={isDeleting || isUpdating}
                className="edit-button"
              >
                Edit
              </button>
            )}
            <button
              onClick={handleDelete}
              disabled={isDeleting || isUpdating}
              className="delete-button"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </>
      )}

      {error && <div className="error">{error}</div>}
    </div>
  );
};
