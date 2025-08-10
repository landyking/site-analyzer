// Lightweight auth helpers for client-side checks

export function getAccessToken(): string | null {
  try {
    return localStorage.getItem('access_token');
  } catch {
    return null;
  }
}

function base64UrlDecode(input: string): string {
  // Convert base64url to base64
  let base64 = input.replace(/-/g, '+').replace(/_/g, '/');
  // Pad with '='
  const pad = base64.length % 4;
  if (pad) {
    base64 += '='.repeat(4 - pad);
  }
  try {
    return atob(base64);
  } catch {
  // In browsers, atob should exist. If it fails, return empty string.
  return '';
  }
}

export function parseJwt<T = unknown>(token: string | null): T | null {
  if (!token) return null;
  const parts = token.split('.');
  if (parts.length < 2) return null;
  try {
    const json = base64UrlDecode(parts[1]);
    return JSON.parse(json) as T;
  } catch {
    return null;
  }
}

export function isAdmin(): boolean {
  const token = getAccessToken();
  const payload = parseJwt<{ admin?: boolean }>(token);
  return !!payload?.admin;
}
