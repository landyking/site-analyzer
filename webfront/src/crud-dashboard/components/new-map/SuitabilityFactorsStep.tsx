import { forwardRef, useImperativeHandle, useMemo, useState } from 'react';
import { VictoryChart, VictoryHistogram, VictoryAxis, VictoryTheme } from 'victory';
import TextField from '@mui/material/TextField';
import Slider from '@mui/material/Slider';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Divider from '@mui/material/Divider';


export type SuitabilityFactorRangeItem = { start: number; end: number; points: number };
export type SuitabilityFactorItem = { kind: string; weight: number; ranges: SuitabilityFactorRangeItem[] };
export type SuitabilityFactorsValue = SuitabilityFactorItem[];

export interface SuitabilityFactorsStepProps {
  value: SuitabilityFactorsValue;
  onChange: (value: SuitabilityFactorsValue) => void;
  districtCode: string;
}

export type SuitabilityFactorsStepHandle = { validate: () => boolean };

const ALL_FACTORS = [
  { code: 'solar', label: 'Annual solar radiation' },
  { code: 'temperature', label: 'Annual temperature' },
  { code: 'roads', label: 'Proximity to roads' },
  { code: 'powerlines', label: 'Proximity to powerlines' },
  { code: 'slope', label: 'Slope' },
];

// Static histogram data for demonstration
const HISTOGRAM_DATA: Record<string, number[]> = {
  solar: [3, 4, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 9, 8, 7, 6, 5],
  temperature: [10, 12, 13, 15, 18, 20, 22, 23, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 2, 3, 4, 5],
  slope: [1, 2, 2, 3, 4, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 9, 8, 7],
};


// --- Subcomponents ---

function FactorSelector({ selectionError }: { selectionError?: string }) {
  return (
    <FormControl error={Boolean(selectionError)}>
      <FormHelperText>
        {selectionError ?? 'Select suitability factors; each selected factor requires a weight and scoring rules.'}
      </FormHelperText>
    </FormControl>
  );
}

function FactorWeight({
  selected,
  error,
  onChange,
}: {
  selected: SuitabilityFactorItem;
  error?: string;
  onChange: (w: number | '') => void;
}) {
  return (
    <FormControl error={Boolean(error)} sx={{ maxWidth: 400, minWidth: 260, pl: 2, pr: 2 }}>
      <Stack direction="row" alignItems="center" spacing={2} sx={{ width: '100%' }}>
        <Typography sx={{ whiteSpace: 'nowrap' }}>Weight: {Number.isFinite(selected.weight) ? selected.weight : ''}</Typography>
        <Slider
          value={Number.isFinite(selected.weight) ? selected.weight : 1}
          min={1}
          max={10}
          step={1}
          marks
          valueLabelDisplay="auto"
          onChange={(_, newValue) => onChange(Number(newValue))}
          sx={{ flex: 1, minWidth: 120 }}
          defaultValue={1}
        />
      </Stack>
      {error && <FormHelperText>{error}</FormHelperText>}
    </FormControl>
  );
}

function FactorHistogram({ code }: { code: string }) {
  if (!(code === 'solar' || code === 'temperature' || code === 'slope')) return null;
  return (
    <Stack spacing={1} alignItems="flex-start">
      <Typography variant="subtitle2" sx={{ fontWeight: 500, mb: 0.5 }}>
        Data distribution
      </Typography>
      <Paper variant="outlined" sx={{ p: 1, background: '#fafbfc', maxWidth: 620 }}>
        <VictoryChart
          theme={VictoryTheme.material}
          domainPadding={{ x: 10 }}
          height={160}
          width={600}
          padding={{ top: 20, bottom: 40, left: 50, right: 20 }}
        >
          <VictoryAxis
            label="Value"
            style={{ axisLabel: { padding: 28, fontSize: 12 } }}
          />
          <VictoryAxis
            dependentAxis
            label="Count"
            style={{ axisLabel: { padding: 32, fontSize: 12 } }}
          />
          <VictoryHistogram
            data={HISTOGRAM_DATA[code].map((x) => ({ x }))}
            bins={10}
            style={{ data: { fill: '#1976d2', opacity: 0.7 } }}
          />
        </VictoryChart>
      </Paper>
    </Stack>
  );
}

function FactorScoringRules({
  ranges,
  error,
  onUpdate,
  onAdd,
  onRemove,
}: {
  ranges: SuitabilityFactorRangeItem[];
  error?: Array<{ start?: string; end?: string; points?: string }>;
  onUpdate: (idx: number, patch: Partial<SuitabilityFactorRangeItem>) => void;
  onAdd: () => void;
  onRemove: (idx: number) => void;
}) {
  return (
    <>
      <Typography variant="subtitle2" sx={{ mt: 1 }}>Scoring rules</Typography>
      {ranges.length === 0 && error && (
        <FormHelperText error sx={{ mb: 1, color: 'error.main' }}>
          At least one scoring rule is required. Please add one.
        </FormHelperText>
      )}
      <Stack spacing={1}>
        {ranges.map((r, idx) => {
          const re = error?.[idx] || {};
          return (
            <Stack key={idx} direction="row" spacing={2} alignItems="center">
              <FormControl error={Boolean(re.start)} sx={{ width: 180 }}>
                <TextField
                  required
                  label="Start"
                  type="number"
                  value={Number.isFinite(r.start) ? r.start : ''}
                  onChange={(e) => onUpdate(idx, { start: e.target.value === '' ? Number.NaN : Number(e.target.value) })}
                  error={Boolean(re.start)}
                  helperText={re.start}
                  inputProps={{ step: 'any' }}
                />
              </FormControl>
              <FormControl error={Boolean(re.end)} sx={{ width: 180 }}>
                <TextField
                  required
                  label="End"
                  type="number"
                  value={Number.isFinite(r.end) ? r.end : ''}
                  onChange={(e) => onUpdate(idx, { end: e.target.value === '' ? Number.NaN : Number(e.target.value) })}
                  error={Boolean(re.end)}
                  helperText={re.end}
                  inputProps={{ step: 'any' }}
                />
              </FormControl>
              <FormControl error={Boolean(re.points)} sx={{ width: 180 }}>
                <TextField
                  required
                  label="Points"
                  type="number"
                  value={Number.isFinite(r.points) ? r.points : ''}
                  onChange={(e) => onUpdate(idx, { points: e.target.value === '' ? Number.NaN : Number(e.target.value) })}
                  error={Boolean(re.points)}
                  helperText={re.points}
                  inputProps={{ step: 1 }}
                />
              </FormControl>
              <IconButton aria-label="delete" onClick={() => onRemove(idx)}>
                <DeleteIcon />
              </IconButton>
            </Stack>
          );
        })}
        <IconButton aria-label="add" color="primary" onClick={onAdd}>
          <AddIcon />
        </IconButton>
      </Stack>
    </>
  );
}

function useSuitabilityErrors(value: SuitabilityFactorsValue) {
  const [errors, setErrors] = useState<Record<string, { weight?: string; ranges?: Array<{ start?: string; end?: string; points?: string }> }>>({});
  const [selectionError, setSelectionError] = useState<string | undefined>();

  function validate() {
    let ok = true;
    const next: Record<string, { weight?: string; ranges?: Array<{ start?: string; end?: string; points?: string }> }> = {};
    if (value.length === 0) {
      ok = false;
      setSelectionError('Select at least one suitability factor');
    } else {
      setSelectionError(undefined);
    }
    for (const item of value) {
      const e: { weight?: string; ranges?: Array<{ start?: string; end?: string; points?: string }> } = {};
      if (!Number.isFinite(item.weight)) {
        e.weight = 'Weight is required and must be a number';
        ok = false;
      } else if (item.weight <= 0 || item.weight > 10) {
        e.weight = 'Weight must be in (0, 10]';
        ok = false;
      }
      if (!item.ranges.length) {
        e.ranges = [{ start: 'Required', end: 'Required', points: 'Required' }];
        ok = false;
      } else {
        e.ranges = item.ranges.map((r) => {
          const re: { start?: string; end?: string; points?: string } = {};
          if (!Number.isFinite(r.start)) re.start = 'Required';
          if (!Number.isFinite(r.end)) re.end = 'Required';
          if (!Number.isFinite(r.points)) re.points = 'Required';
          if (re.start || re.end || re.points) ok = false;
          return re;
        });
      }
      if (e.weight || e.ranges?.some((x) => x.start || x.end || x.points)) next[item.kind] = e;
    }
    setErrors(next);
    return ok;
  }

  function clearWeightError(kind: string) {
    setErrors((prev) => ({ ...prev, [kind]: { ...prev[kind], weight: undefined } }));
  }

  function clearRangeError(kind: string, idx: number) {
    setErrors((prev) => {
      const pe = { ...(prev[kind] || {}) };
      if (pe.ranges && pe.ranges[idx]) pe.ranges[idx] = {};
      return { ...prev, [kind]: pe };
    });
  }

  return { errors, selectionError, validate, clearWeightError, clearRangeError };
}

function useSuitabilitySelection(value: SuitabilityFactorsValue, onChange: (v: SuitabilityFactorsValue) => void, setSelectionError: (e: string | undefined) => void) {
  function toggle(kind: string, checked: boolean) {
    const idx = value.findIndex((v) => v.kind === kind);
    const next = [...value];
    if (checked && idx === -1) {
      next.push({ kind, weight: 1, ranges: [{ start: Number.NaN, end: Number.NaN, points: Number.NaN }] });
      setSelectionError(undefined);
    } else if (!checked && idx >= 0) {
      next.splice(idx, 1);
    }
    onChange(next);
  }

  function updateWeight(kind: string, w: number | '', clearWeightError: (kind: string) => void) {
    const next = value.map((v) => (v.kind === kind ? { ...v, weight: w === '' ? Number.NaN : Number(w) } : v));
    onChange(next);
    clearWeightError(kind);
  }

  function addRange(kind: string) {
    const next = value.map((v) => (v.kind === kind ? { ...v, ranges: [...v.ranges, { start: Number.NaN, end: Number.NaN, points: Number.NaN }] } : v));
    onChange(next);
  }

  function removeRange(kind: string, idx: number) {
    const next = value.map((v) => {
      if (v.kind !== kind) return v;
      const ranges = [...v.ranges];
      ranges.splice(idx, 1);
      return { ...v, ranges };
    });
    onChange(next);
  }

  function updateRange(kind: string, idx: number, patch: Partial<SuitabilityFactorRangeItem>, clearRangeError: (kind: string, idx: number) => void) {
    const next = value.map((v) => {
      if (v.kind !== kind) return v;
      const ranges = [...v.ranges];
      const current = ranges[idx] ?? { start: Number.NaN, end: Number.NaN, points: Number.NaN };
      ranges[idx] = { ...current, ...patch } as SuitabilityFactorRangeItem;
      return { ...v, ranges };
    });
    onChange(next);
    clearRangeError(kind, idx);
  }

  return { toggle, updateWeight, addRange, removeRange, updateRange };
}


const SuitabilityFactorsStepInner = forwardRef<SuitabilityFactorsStepHandle, SuitabilityFactorsStepProps>(
  ({ value, onChange, districtCode }, ref) => {
    const { errors, selectionError, validate, clearWeightError, clearRangeError } = useSuitabilityErrors(value);
    const { toggle, updateWeight, addRange, removeRange, updateRange } = useSuitabilitySelection(value, onChange, (e) => {});
    const selectedMap = useMemo(() => new Map(value.map((v) => [v.kind, v])), [value]);

    function handleToggle(kind: string, checked: boolean) {
      toggle(kind, checked);
    }
    function handleUpdateWeight(kind: string, w: number | '') {
      updateWeight(kind, w, clearWeightError);
    }
    function handleUpdateRange(kind: string, idx: number, patch: Partial<SuitabilityFactorRangeItem>) {
      updateRange(kind, idx, patch, clearRangeError);
    }

    useImperativeHandle(ref, () => ({ validate }));

    return (
      <Stack spacing={2}>
        <FactorSelector selectionError={selectionError} />
        {ALL_FACTORS.map((opt) => {
          const selected = selectedMap.get(opt.code);
          const err = errors[opt.code];
          return (
            <Paper key={opt.code} variant="outlined" sx={{ p: 2 }}>
              <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                <FormControlLabel
                  control={<Checkbox checked={Boolean(selected)} onChange={(_, c) => handleToggle(opt.code, c)} />}
                  label={<Typography variant="subtitle1">{opt.label}</Typography>}
                />
                {selected && (
                  <FactorWeight
                    selected={selected}
                    error={err?.weight}
                    onChange={(w) => handleUpdateWeight(opt.code, w)}
                  />
                )}
              </Stack>
              {selected && (
                <Stack spacing={2} sx={{ pl: 5, pt: 1 }}>
                  <Divider flexItem />
                  <FactorHistogram code={opt.code} />
                  <FactorScoringRules
                    ranges={selected.ranges}
                    error={err?.ranges}
                    onUpdate={(idx, patch) => handleUpdateRange(opt.code, idx, patch)}
                    onAdd={() => addRange(opt.code)}
                    onRemove={(idx) => removeRange(opt.code, idx)}
                  />
                </Stack>
              )}
            </Paper>
          );
        })}
      </Stack>
    );
  },
);

const SuitabilityFactorsStep = forwardRef<SuitabilityFactorsStepHandle, SuitabilityFactorsStepProps>((props, ref) => {
  return <SuitabilityFactorsStepInner {...props} ref={ref} />;
});

export default SuitabilityFactorsStep;
