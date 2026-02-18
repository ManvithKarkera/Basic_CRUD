// Type definitions for Task domain model

export enum TaskStatus {
  TODO = 'TODO',
  IN_PROGRESS = 'IN_PROGRESS',
  DONE = 'DONE'
}

export interface Task {
  id: number;
  sno: number;  // Backend uses 'sno' as the ID field
  title: string;
  desc: string;
  status: TaskStatus;
  date_created: string;
}

export interface CreateTaskRequest {
  title: string;
  status?: TaskStatus;
}

export interface UpdateTaskRequest {
  title?: string;
  status?: TaskStatus;
}

export interface APIError {
  error: string;
}

// Valid state transitions defined by backend
export const VALID_TRANSITIONS: Record<TaskStatus, TaskStatus[]> = {
  [TaskStatus.TODO]: [TaskStatus.IN_PROGRESS, TaskStatus.DONE],
  [TaskStatus.IN_PROGRESS]: [TaskStatus.DONE],
  [TaskStatus.DONE]: [] // Terminal state
};

export function canTransitionTo(currentStatus: TaskStatus, newStatus: TaskStatus): boolean {
  return VALID_TRANSITIONS[currentStatus].includes(newStatus);
}

export function getAvailableTransitions(currentStatus: TaskStatus): TaskStatus[] {
  return VALID_TRANSITIONS[currentStatus];
}
