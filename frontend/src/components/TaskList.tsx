import React, { useState, useEffect } from 'react';
import { Task } from '../types/Task';
import { todoApi } from '../api/todoApi';
import { TaskItem } from './TaskItem';

export const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await todoApi.getAllTodos();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  if (isLoading) {
    return <div className="loading">Loading tasks...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error">{error}</p>
        <button onClick={fetchTasks}>Retry</button>
      </div>
    );
  }

  if (tasks.length === 0) {
    return <div className="empty-state">No tasks yet. Create one to get started!</div>;
  }

  return (
    <div className="task-list">
      <h2>Tasks ({tasks.length})</h2>
      <div className="tasks-container">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onTaskUpdated={fetchTasks}
            onTaskDeleted={fetchTasks}
          />
        ))}
      </div>
    </div>
  );
};
