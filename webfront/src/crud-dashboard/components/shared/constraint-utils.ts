export type ConstraintDisplayItem = {
  kind: string;
  label?: string;
  value?: number;
  [key: string]: unknown;
};

export function normalizeConstraints(input: unknown[]): ConstraintDisplayItem[] {
  if (!Array.isArray(input)) return [];
  const out: ConstraintDisplayItem[] = [];
  for (const raw of input) {
    if (!raw || typeof raw !== 'object') continue;
    const rec = raw as Record<string, unknown>;
    const kind = rec.kind != null ? String(rec.kind) : '';
    if (!kind) continue;
    const label = typeof rec.label === 'string' ? rec.label : undefined;
  const v = (rec as { [k: string]: unknown }).value ?? (rec as { [k: string]: unknown }).distance ?? (rec as { [k: string]: unknown })['distance_m']; // distance_m may exist from backend
    const num = typeof v === 'number' ? v : Number(v);
    const value = Number.isFinite(num) ? num : undefined;
    out.push({ kind, label, value });
  }
  return out;
}
