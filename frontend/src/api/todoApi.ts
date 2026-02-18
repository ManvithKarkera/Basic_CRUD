import { Task, CreateTaskRequest, UpdateTaskRequest, APIError } from '../types/Task';

// Use empty string for dev (Vite proxy) or full URL for production
const API_BASE_URL = import.meta.env.PROD ? 'http://127.0.0.1:5000' : '';

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData: APIError = await response.json();
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  async getAllTodos(): Promise<Task[]> {
    const todos = await this.request<Task[]>('/todos');
    // Map sno to id for frontend convenience
    return todos.map(todo => ({ ...todo, id: todo.sno }));
  }

  async getTodoById(id: number): Promise<Task> {
    const todo = await this.request<Task>(`/todos/${id}`);
    return { ...todo, id: todo.sno };
  }

  async createTodo(data: CreateTaskRequest): Promise<Task> {
    const todo = await this.request<Task>('/todos', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { ...todo, id: todo.sno };
  }

  async updateTodo(id: number, data: UpdateTaskRequest): Promise<Task> {
    const todo = await this.request<Task>(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return { ...todo, id: todo.sno };
  }

  async deleteTodo(id: number): Promise<void> {
    return this.request<void>(`/todos/${id}`, {
      method: 'DELETE',
    });
  }
}

export const todoApi = new APIClient(API_BASE_URL);
