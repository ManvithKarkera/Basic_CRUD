import React, { useState } from 'react';
import { CreateTask } from './components/CreateTask';
import { TaskList } from './components/TaskList';
import './App.css';

const App: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTaskCreated = () => {
    // Trigger TaskList refresh by changing key
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Task Management</h1>
        <p>A structured Flask API with React frontend</p>
      </header>

      <main className="app-main">
        <CreateTask onTaskCreated={handleTaskCreated} />
        <TaskList key={refreshKey} />
      </main>

      <footer className="app-footer">
        <small>
          Status transitions: TODO → IN_PROGRESS → DONE (DONE is terminal)
        </small>
      </footer>
    </div>
  );
};

export default App;
