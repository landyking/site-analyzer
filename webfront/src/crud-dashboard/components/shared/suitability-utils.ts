export type SuitabilityDisplayRange = {
  start?: number; // inclusive lower bound
  end?: number;   // exclusive upper bound
  points?: number;
};

export type SuitabilityDisplayFactor = {
  kind: string;
  label?: string;
  weight?: number;
  ranges: SuitabilityDisplayRange[];
};

export const SUITABILITY_LABELS: Record<string, string> = {
  solar: 'Mean annual solar radiation',
  temperature: 'Mean annual temperature',
  roads: 'Road distances',
  powerlines: 'Powerline distances',
  slope: 'Land slope',
};

// Accepts both old format (with ranges) and new format (with breakpoints/points)
export function normalizeSuitabilityFactors(input: unknown[]): SuitabilityDisplayFactor[] {
  if (!Array.isArray(input)) return [];

  const out: SuitabilityDisplayFactor[] = [];
  for (const raw of input) {
    if (!raw || typeof raw !== 'object') continue;
    const rec = raw as Record<string, unknown>;
    const kind = rec.kind != null ? String(rec.kind) : '';
    if (!kind) continue;
    const label = typeof rec.label === 'string' ? rec.label : undefined;
    const weightNum = typeof rec.weight === 'number' ? rec.weight : Number(rec.weight);
    const weight = Number.isFinite(weightNum) ? weightNum : undefined;

    // If ranges already provided, prefer them
  const recIdx = rec as { [k: string]: unknown };
  const rangesRaw = Array.isArray(recIdx['ranges']) ? (recIdx['ranges'] as unknown[]) : undefined;
    if (rangesRaw) {
      const ranges: SuitabilityDisplayRange[] = [];
      for (const r of rangesRaw) {
        if (!r || typeof r !== 'object') continue;
        const rr = r as Record<string, unknown>;
        const sNum = typeof rr.start === 'number' ? rr.start : Number(rr.start);
        const eNum = typeof rr.end === 'number' ? rr.end : Number(rr.end);
        const pNum = typeof rr.points === 'number' ? rr.points : Number(rr.points);
        const start = Number.isFinite(sNum) ? sNum : undefined;
        const end = Number.isFinite(eNum) ? eNum : undefined;
        const points = Number.isFinite(pNum) ? pNum : undefined;
        ranges.push({ start, end, points });
      }
      out.push({ kind, label, weight, ranges });
      continue;
    }

    // Otherwise, try breakpoints/points
    const breakpoints = Array.isArray(recIdx['breakpoints'])
      ? ((recIdx['breakpoints'] as unknown[])
          .map((n) => Number(n))
          .filter((n) => Number.isFinite(n)) as number[])
      : [];
    const pointsArr = Array.isArray(recIdx['points']) ? (recIdx['points'] as unknown[]).map((n) => Number(n)) : [];

    if (breakpoints.length) {
      const sorted = [...breakpoints].sort((a, b) => a - b);
      const ranges: SuitabilityDisplayRange[] = [];
      let last = Number.NEGATIVE_INFINITY;
      for (let i = 0; i < sorted.length; i++) {
        const end = sorted[i];
        const pts = Number.isFinite(pointsArr[i]) ? (pointsArr[i] as number) : undefined;
        ranges.push({ start: Number.isFinite(last) ? last : undefined, end, points: pts });
        last = end;
      }
      // tail interval [last, +Inf)
      const tailPts = Number.isFinite(pointsArr[pointsArr.length - 1]) ? (pointsArr[pointsArr.length - 1] as number) : undefined;
      ranges.push({ start: Number.isFinite(last) ? last : undefined, end: undefined, points: tailPts });
      out.push({ kind, label, weight, ranges });
      continue;
    }

    // No usable data; still include the factor with empty ranges to preserve intent
    out.push({ kind, label, weight, ranges: [] });
  }

  return out;
}
