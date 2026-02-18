# Task Management Frontend

Minimal React TypeScript frontend for the Flask Task Management API.

## Architecture

### Folder Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── todoApi.ts        # API client for backend communication
│   ├── components/
│   │   ├── CreateTask.tsx    # Task creation form
│   │   ├── TaskList.tsx      # Task list display with loading/error states
│   │   └── TaskItem.tsx      # Individual task with status transitions
│   ├── types/
│   │   └── Task.ts           # Type definitions and state machine
│   ├── App.tsx               # Main application component
│   ├── App.css               # Basic styling
│   └── main.tsx              # Application entry point
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Design Principles

### No Business Logic Duplication

- **Frontend does NOT re-implement validation**
- **Frontend does NOT re-implement state transition rules**
- Frontend reflects backend constraints in UI (disables invalid transitions)
- Backend remains source of truth for all business rules

### Type Safety

All data is strictly typed:

```typescript
enum TaskStatus {
  TODO = 'TODO',
  IN_PROGRESS = 'IN_PROGRESS',
  DONE = 'DONE'
}

interface Task {
  id: number;
  title: string;
  status: TaskStatus;
  date_created: string;
}
```

### State Machine Visualization

Frontend uses backend's state machine definition:

```typescript
const VALID_TRANSITIONS: Record<TaskStatus, TaskStatus[]> = {
  TODO: [IN_PROGRESS, DONE],
  IN_PROGRESS: [DONE],
  DONE: [] // Terminal state
};
```

This is **documentation of backend behavior**, not frontend logic.

### Error Handling

- All API errors displayed to user
- Backend error messages shown directly
- Loading states prevent duplicate requests
- Network failures handled gracefully

## Components

### CreateTask

- Form for creating new tasks
- Local validation (non-empty title)
- Disables form during submission
- Shows backend error messages

### TaskList

- Fetches all tasks on mount
- Loading state while fetching
- Error state with retry button
- Empty state when no tasks

### TaskItem

- Displays task details
- Shows only valid status transitions as buttons
- Disables buttons during update/delete
- Confirms before deletion
- Shows backend error messages

## API Client

Centralized API communication:

```typescript
class APIClient {
  async getAllTodos(): Promise<Task[]>
  async getTodoById(id: number): Promise<Task>
  async createTodo(data: CreateTaskRequest): Promise<Task>
  async updateTodo(id: number, data: UpdateTaskRequest): Promise<Task>
  async deleteTodo(id: number): Promise<void>
}
```

- Type-safe request/response handling
- Automatic JSON conversion
- HTTP error handling with backend error messages
- Single source for API base URL

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Flask backend running on `http://127.0.0.1:5000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Frontend runs at `http://localhost:3000`

**Note**: Vite dev server proxies `/todos` requests to Flask backend at `http://127.0.0.1:5000`

### Type Checking

```bash
npm run type-check
```

### Production Build

```bash
npm run build
```

Output: `dist/` directory

### Preview Production Build

```bash
npm run preview
```

## Backend Integration

### Expected Backend Endpoints

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| GET | `/todos` | - | `Task[]` |
| POST | `/todos` | `CreateTaskRequest` | `Task` |
| GET | `/todos/:id` | - | `Task` |
| PUT | `/todos/:id` | `UpdateTaskRequest` | `Task` |
| DELETE | `/todos/:id` | - | 204 No Content |

### CORS Configuration

Backend must allow requests from `http://localhost:3000` during development.

Add to Flask backend:

```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

Or manually:

```python
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
```

## Technology Stack

- **React 18**: Functional components with hooks
- **TypeScript 5**: Strict type checking
- **Vite 5**: Fast development and build tooling
- **Native fetch API**: No axios dependency for simplicity

## What This Frontend Does NOT Do

- **No Redux/MobX**: Local state with `useState`
- **No routing**: Single page application
- **No UI library**: Plain CSS for clarity
- **No form library**: Native form handling
- **No client-side validation beyond empty checks**: Backend is source of truth
- **No optimistic updates**: Wait for backend confirmation
- **No caching**: Fetch fresh data on every mount

## Extending the Frontend

### Add New Field

1. Update `Task` interface in `types/Task.ts`
2. Update API client request/response types
3. Update components to display/edit new field

### Add Filtering

1. Add filter state in `TaskList`
2. Filter tasks array before rendering
3. Add UI controls for filter selection

### Add Pagination

1. Update `todoApi.getAllTodos()` to accept page parameters
2. Add page state in `TaskList`
3. Add pagination controls

## Tradeoffs

### Simplicity Over Features

- No advanced state management (acceptable for small app)
- No offline support (requires backend)
- No optimistic UI updates (ensures consistency)
- Refetch after every mutation (simple, correct)

### Type Safety Over Flexibility

- Strict TypeScript configuration
- All API responses typed
- No `any` types allowed

### Clarity Over Abstraction

- No generic components for forms
- No higher-order components
- Direct, readable code

---

**Last Updated**: February 19, 2026
