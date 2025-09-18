// Shared table formatting utilities (non-React functions)
export function formatDate(value?: string | null) {
  if (!value) return '-';
  try {
    const d = new Date(value);
    return new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).format(d);
  } catch {
    return value as string;
  }
}

export function formatElapsed(start?: string | null, end?: string | null) {
  const startMs = start ? Date.parse(start) : NaN;
  const endMs = end ? Date.parse(end) : Date.now();
  if (Number.isNaN(startMs) || Number.isNaN(endMs)) return '-';
  const ms = Math.max(0, endMs - startMs);
  const minutes = Math.floor(ms / 60000);
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (hours > 0) return `${hours}h ${remainingMinutes}m`;
  if (minutes > 0) return `${minutes}m`;
  const seconds = Math.floor(ms / 1000);
  return `${seconds}s`;
}
