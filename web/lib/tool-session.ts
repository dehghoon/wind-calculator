// Kept only in memory; never URLs, localStorage or rendered HTML.
let token: string | null = null;
export function setToolSession(value: string | null) { token = value; }
export function toolAuthorization(): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}
