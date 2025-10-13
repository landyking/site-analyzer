// Lightweight auth helpers for client-side checks

/**
 * Retrieves the access token from localStorage.
 * @returns The access token string or null if not found or error occurs.
 */
export function getAccessToken(): string | null {
  try {
    return localStorage.getItem('access_token');
  } catch {
    return null;
  }
}

/**
 * Decodes a base64url encoded string to a regular string.
 * @param input - The base64url encoded string to decode.
 * @returns The decoded string, or empty string if decoding fails.
 */
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

/**
 * Parses a JWT token and returns its payload.
 * @template T - The type of the payload.
 * @param token - The JWT token string or null.
 * @returns The parsed payload or null if parsing fails.
 */
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

/**
 * Checks if the current user has admin privileges based on the JWT token.
 * @returns True if the user is an admin, false otherwise.
 */
export function isAdmin(): boolean {
  const token = getAccessToken();
  const payload = parseJwt<{ admin?: boolean }>(token);
  return !!payload?.admin;
}

/**
 * Checks if the user is logged in by verifying the presence of an access token.
 * @returns True if a non-empty access token exists, false otherwise.
 */
export function isLoggedIn(): boolean {
  const token = getAccessToken();
  return !!token && token.trim() !== '';
}
