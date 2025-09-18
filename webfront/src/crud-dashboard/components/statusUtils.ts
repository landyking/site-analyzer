// Shared status utilities for map tasks (admin + user views)

export const MAP_TASK_STATUS = {
  PENDING: 1,
  PROCESSING: 2,
  SUCCESS: 3,
  FAILURE: 4,
  CANCELLED: 5,
} as const;

export type MapTaskStatusCode = typeof MAP_TASK_STATUS[keyof typeof MAP_TASK_STATUS];

export interface StatusOption {
  code: MapTaskStatusCode;
  value: string; // internal filter value
  label: string; // UI label
}

export const mapTaskStatusOptions: StatusOption[] = [
  { code: MAP_TASK_STATUS.PENDING, value: 'pending', label: 'Pending' },
  { code: MAP_TASK_STATUS.PROCESSING, value: 'processing', label: 'Processing' },
  { code: MAP_TASK_STATUS.SUCCESS, value: 'success', label: 'Success' },
  { code: MAP_TASK_STATUS.FAILURE, value: 'failure', label: 'Failure' },
  { code: MAP_TASK_STATUS.CANCELLED, value: 'cancelled', label: 'Cancelled' },
];

export function mapStatusFilterValueToCode(filter: string | 'all'): MapTaskStatusCode | undefined {
  if (filter === 'all') return undefined;
  const found = mapTaskStatusOptions.find(o => o.value === filter);
  return found?.code;
}

export function mapTaskStatusColor(desc?: string | null): 'default' | 'success' | 'error' | 'warning' | 'info' {
  const label = (desc || '').toLowerCase();
  if (label.includes('success') || label.includes('complete')) return 'success';
  if (label.includes('fail') || label.includes('error')) return 'error';
  if (label.includes('cancel')) return 'warning';
  if (label.includes('process') || label.includes('running')) return 'info';
  if (label.includes('pending') || label.includes('queue')) return 'default';
  return 'default';
}

// ---- User Status Utilities ----
export const USER_STATUS = {
  ACTIVE: 1,
  LOCKED: 2,
} as const;

export type UserStatusCode = typeof USER_STATUS[keyof typeof USER_STATUS];

export function userStatusLabel(code?: number | null) {
  switch (code) {
    case USER_STATUS.ACTIVE: return 'Active';
    case USER_STATUS.LOCKED: return 'Locked';
    default: return '-';
  }
}

export function userStatusColor(code?: number | null): 'success' | 'warning' | 'default' {
  switch (code) {
    case USER_STATUS.ACTIVE: return 'success';
    case USER_STATUS.LOCKED: return 'warning';
    default: return 'default';
  }
}

export interface UserStatusFilterOption { value: 'all' | 'active' | 'locked'; label: string; }
export const userStatusFilterOptions: UserStatusFilterOption[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'locked', label: 'Locked' },
];

export function userStatusFilterValueToCode(filter: 'all' | 'active' | 'locked'): UserStatusCode | undefined {
  if (filter === 'all') return undefined;
  return filter === 'active' ? USER_STATUS.ACTIVE : USER_STATUS.LOCKED;
}
