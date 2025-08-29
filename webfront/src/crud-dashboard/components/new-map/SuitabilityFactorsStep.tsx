import { forwardRef, useImperativeHandle, useMemo, useState } from 'react';
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
}

export type SuitabilityFactorsStepHandle = { validate: () => boolean };

const ALL_FACTORS = [
  { code: 'solar', label: 'Annual solar radiation' },
  { code: 'temperature', label: 'Annual temperature' },
  { code: 'roads', label: 'Proximity to roads' },
  { code: 'powerlines', label: 'Proximity to powerlines' },
  { code: 'slope', label: 'Slope' },
];

const SuitabilityFactorsStep = forwardRef<SuitabilityFactorsStepHandle, SuitabilityFactorsStepProps>(
  ({ value, onChange }, ref) => {
  const [errors, setErrors] = useState<Record<string, { weight?: string; ranges?: Array<{ start?: string; end?: string; points?: string }> }>>({});
  const [selectionError, setSelectionError] = useState<string | undefined>();

    const selectedMap = useMemo(() => new Map(value.map((v) => [v.kind, v])), [value]);

    useImperativeHandle(ref, () => ({
      validate: () => {
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
      },
    }));

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

    function updateWeight(kind: string, w: number | '') {
      const next = value.map((v) => (v.kind === kind ? { ...v, weight: w === '' ? Number.NaN : Number(w) } : v));
      onChange(next);
      setErrors((prev) => ({ ...prev, [kind]: { ...prev[kind], weight: undefined } }));
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

    function updateRange(kind: string, idx: number, patch: Partial<SuitabilityFactorRangeItem>) {
      const next = value.map((v) => {
        if (v.kind !== kind) return v;
        const ranges = [...v.ranges];
        const current = ranges[idx] ?? { start: Number.NaN, end: Number.NaN, points: Number.NaN };
        ranges[idx] = { ...current, ...patch } as SuitabilityFactorRangeItem;
        return { ...v, ranges };
      });
      onChange(next);
      setErrors((prev) => {
        const pe = { ...(prev[kind] || {}) };
        if (pe.ranges && pe.ranges[idx]) pe.ranges[idx] = {};
        return { ...prev, [kind]: pe };
      });
    }

    return (
      <Stack spacing={2}>
        <FormControl error={Boolean(selectionError)}>
          <FormHelperText>
            {selectionError ?? 'Select suitability factors; each selected factor requires a weight and scoring rules.'}
          </FormHelperText>
        </FormControl>
        {ALL_FACTORS.map((opt) => {
          const selected = selectedMap.get(opt.code);
          const err = errors[opt.code];
          return (
            <Paper key={opt.code} variant="outlined" sx={{ p: 2 }}>
              <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                <FormControlLabel
                  control={<Checkbox checked={Boolean(selected)} onChange={(_, c) => toggle(opt.code, c)} />}
                  label={<Typography variant="subtitle1">{opt.label}</Typography>}
                />

                {selected && (
                  <FormControl error={Boolean(err?.weight)} sx={{ maxWidth: 400, minWidth: 260, pl: 2, pr: 2 }}>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ width: '100%' }}>
                      <Typography sx={{ whiteSpace: 'nowrap' }}>Weight: {Number.isFinite(selected.weight) ? selected.weight : ''}</Typography>
                      <Slider
                        value={Number.isFinite(selected.weight) ? selected.weight : 1}
                        min={1}
                        max={10}
                        step={1}
                        marks
                        valueLabelDisplay="auto"
                        onChange={(_, newValue) => updateWeight(opt.code, Number(newValue))}
                        sx={{ flex: 1, minWidth: 120 }}
                        defaultValue={1}
                      />
                    </Stack>
                    {err?.weight && (
                      <FormHelperText>{err.weight}</FormHelperText>
                    )}
                  </FormControl>
                )}
              </Stack>

              {selected && (
                <Stack spacing={2} sx={{ pl: 5, pt: 1 }}>
                  <Divider flexItem />
                  <Typography variant="subtitle2">Scoring rules</Typography>

                  <Stack spacing={1}>
                    {selected.ranges.map((r, idx) => {
                      const re = err?.ranges?.[idx] || {};
                      return (
                        <Stack key={idx} direction="row" spacing={2} alignItems="center">
                          <FormControl error={Boolean(re.start)} sx={{ width: 180 }}>
                            <TextField
                              required
                              label="Start"
                              type="number"
                              value={Number.isFinite(r.start) ? r.start : ''}
                              onChange={(e) => updateRange(opt.code, idx, { start: e.target.value === '' ? Number.NaN : Number(e.target.value) })}
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
                              onChange={(e) => updateRange(opt.code, idx, { end: e.target.value === '' ? Number.NaN : Number(e.target.value) })}
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
                              onChange={(e) => updateRange(opt.code, idx, { points: e.target.value === '' ? Number.NaN : Number(e.target.value) })}
                              error={Boolean(re.points)}
                              helperText={re.points}
                              inputProps={{ step: 1 }}
                            />
                          </FormControl>

                          <IconButton aria-label="delete" onClick={() => removeRange(opt.code, idx)}>
                            <DeleteIcon />
                          </IconButton>
                        </Stack>
                      );
                    })}

                    <IconButton aria-label="add" color="primary" onClick={() => addRange(opt.code)}>
                      <AddIcon />
                    </IconButton>
                  </Stack>
                </Stack>
              )}
            </Paper>
          );
        })}
      </Stack>
    );
  },
);

export default SuitabilityFactorsStep;
