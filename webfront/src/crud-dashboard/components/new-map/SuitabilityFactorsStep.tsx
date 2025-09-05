import Chip from '@mui/material/Chip';
import { forwardRef, useImperativeHandle, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { UserService } from '../../../client/sdk.gen';
import type { DistrictHistogram } from '../../../client/types.gen';

import HistogramCanvas from './HistogramCanvas';
// --- Canvas Histogram Component ---
import TextField from '@mui/material/TextField';
import Slider from '@mui/material/Slider';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
// import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';
// import DeleteIcon from '@mui/icons-material/Delete';
// import Chip from '@mui/material/Chip';
// import InputAdornment from '@mui/material/InputAdornment';
import Button from '@mui/material/Button';
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
  { code: 'solar', label: 'Mean annual solar radiation' },
  { code: 'temperature', label: 'Mean annual temperature' },
  { code: 'slope', label: 'Slope' },
  { code: 'roads', label: 'Proximity to roads' },
  { code: 'powerlines', label: 'Proximity to powerlines' },
];




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
            <Typography variant="body2" color="textSecondary" sx={{ ml: 2, minWidth: 300, whiteSpace: 'nowrap' }}>
              The weight of this factor among all selected factors.
            </Typography>
          </Stack>
          {error && <FormHelperText error>{error}</FormHelperText>}
    </FormControl>
  );
}

function FactorHistogram({ code, histogram }: { code: string; histogram?: DistrictHistogram }) {
  if (!(code === 'solar' || code === 'temperature' || code === 'slope')) return null;
  if (!histogram) return null;
  const { frequency, edges } = histogram;
  // Add tips for interpreting the data values
  let tip = '';
  if (code === 'temperature') {
    tip = 'Tip: A value of -70 means -7°C, 120 means 12°C.';
  } else if (code === 'solar') {
    tip = 'Tip: A value of 115 means 11.5 MJ/m²/day.';
  } else if (code === 'slope') {
    tip = 'Tip: Slope values are in degrees (0–90).';
  }
  return (
    <Stack spacing={0.5} alignItems="flex-start">
      <Stack direction="row" alignItems="center" spacing={1}>
        <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
          Data distribution
        </Typography>
        {tip && (
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            {tip}
          </Typography>
        )}
      </Stack>
      <Paper variant="outlined" sx={{ p: 1, background: '#fafbfc', maxWidth: 620, mt: 0.5 }}>
        <HistogramCanvas frequency={frequency} edges={edges} />
      </Paper>
    </Stack>
  );
}


// Breakpoint-driven Scoring rules component

function BreakpointScoringRules({
  breakpoints,
  points,
  onAddBreakpoint,
  onRemoveBreakpoint,
  onPointsChange,
  error,
  minValue = -Infinity,
  maxValue = Infinity,
}: {
  breakpoints: number[];
  points: number[];
  onAddBreakpoint: (v: number) => void;
  onRemoveBreakpoint: (idx: number) => void;
  onPointsChange: (idx: number, v: number) => void;
  error?: { breakpoints?: string; points?: string[] };
  minValue?: number;
  maxValue?: number;
}) {
  const [input, setInput] = useState('');
  const [inputError, setInputError] = useState<string | null>(null);

  // Generate intervals based on breakpoints
  const sorted = [...breakpoints].sort((a, b) => a - b);
  // Always use positive and negative infinity as interval boundaries
  const intervals = [-Infinity, ...sorted, Infinity];

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    setInput(e.target.value);
    setInputError(null);
  }
  function handleInputConfirm() {
    if (input.trim() === '') {
      // Do nothing if input is empty
      return;
    }
    const v = Number(input);
    if (Number.isNaN(v)) {
      setInputError('Please enter a valid number');
      return;
    }
    if (breakpoints.includes(v)) {
      setInputError('Breakpoint already exists');
      return;
    }
    // Browser will enforce min/max validation, but we keep this as a safety check
    if (minValue !== -Infinity && v <= minValue) {
      setInputError(`Value must be greater than ${minValue}`);
      return;
    }
    if (maxValue !== Infinity && v >= maxValue) {
      setInputError(`Value must be less than ${maxValue}`);
      return;
    }
    onAddBreakpoint(v);
    setInput('');
    setInputError(null);
  }

  return (
    <>
      <Typography variant="h6" sx={{ mt: 1, mb: 0.5, fontWeight: 600, letterSpacing: 0.2 }}>Scoring rules</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Add breakpoints to divide the value range into intervals. Each interval will have a score.
      </Typography>
      {/* Combined row: input + chips */}
      <Stack 
        direction="row" 
        spacing={1} 
        alignItems="center" 
        sx={{ mb: 1, flexWrap: 'wrap', minHeight: 40 }}
      >
        <Typography sx={{ fontWeight: 500, mr: 1 }}>Breakpoints:</Typography>
        <FormControl error={!!inputError} sx={{ width: 140 }}>
          <TextField
            size="small"
            type="number"
            value={input}
            onChange={handleInputChange}
            onKeyDown={e => {
              if (e.key === 'Enter') handleInputConfirm();
            }}
            error={!!inputError}
            placeholder="Enter value"
            inputProps={{ 
              step: 'any',
              min: minValue !== -Infinity ? minValue : undefined,
              max: maxValue !== Infinity ? maxValue : undefined
            }}
          />
          <FormHelperText>
            {inputError || ''}
          </FormHelperText>
        </FormControl>
        <Button
          variant="outlined"
          color="secondary"
          size="small"
          sx={{ minWidth: 28, height: 32, p: 0 }}
          onClick={handleInputConfirm}
          title="add"
        >
          <AddIcon fontSize="inherit" style={{ fontSize: 16 }} />
        </Button>
        {sorted.length > 0 && sorted.map((bp, idx) => (
          <Chip
            key={bp}
            label={bp}
            onDelete={() => onRemoveBreakpoint(idx)}
            sx={{ fontSize: 16, ml: 1 }}
            color="primary"
          />
        ))}
      </Stack>
      {error?.breakpoints && (
        <FormHelperText error sx={{ mb: 1 }}>{error.breakpoints}</FormHelperText>
      )}
      {/* Only show points rows when breakpoints exist */}
      {sorted.length > 0 && (
        <Stack spacing={1}>
          {intervals.slice(0, -1).map((start, idx) => {
            // Build natural language interval description
            let label = '';
            const end = intervals[idx + 1];
            if (start === -Infinity && end !== Infinity) {
              label = `If value ≤ ${end}`;
            } else if (start !== -Infinity && end !== Infinity) {
              label = `If ${start} < value ≤ ${end}`;
            } else if (end === Infinity && start !== -Infinity) {
              label = `If value > ${start}`;
            }
            return (
              <Stack key={idx} direction="row" spacing={2} alignItems="center">
                <Typography sx={{ minWidth: 48, mr: 1 }}>Points:</Typography>
                <FormControl error={!!(error?.points && error.points[idx])} sx={{ width: 120, my: 0 }}>
                  <TextField
                    required
                    type="number"
                    value={Number.isFinite(points[idx]) ? points[idx] : ''}
                    onChange={e => onPointsChange(idx, e.target.value === '' ? NaN : Number(e.target.value))}
                    error={!!(error?.points && error.points[idx])}
                    helperText={error?.points && error.points[idx]}
                    inputProps={{ step: 1, min: 1, max: 10 }}
                    size="small"
                  />
                </FormControl>
                <Chip label={label} color="info" variant="outlined" sx={{ ml: 2, fontSize: 14, my: 0 }} />
              </Stack>
            );
          })}
        </Stack>
      )}
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
      // Debug log to inspect the ranges
      // console.log('Validating item:', item.kind, 'with ranges:', JSON.stringify(item.ranges));
      
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
          // Special handling for -Infinity, Infinity and null
          // In JSON serialization, Infinity becomes null, so we need to handle both
          if (r.start !== -Infinity && r.start !== null && !Number.isFinite(r.start)) re.start = 'Required';
          if (r.end !== Infinity && r.end !== null && !Number.isFinite(r.end)) re.end = 'Required';
          if (!Number.isFinite(r.points)) re.points = 'Required';
          else if (r.points < 1 || r.points > 10) re.points = 'Points must be between 1 and 10';
          
          // Debug log for this range
          /* console.log('Range validation:', {
            start: r.start, 
            end: r.end, 
            points: r.points,
            errors: re
          }); */
          
          if (re.start || re.end || re.points) ok = false;
          return re;
        });
      }
      if (e.weight || e.ranges?.some((x) => x.start || x.end || x.points)) next[item.kind] = e;
    }
    setErrors(next);
    
    // Final validation result
    // console.log('Validation result:', ok, 'Errors:', JSON.stringify(next));
    
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


const SuitabilityFactorsStepInner = forwardRef<SuitabilityFactorsStepHandle, SuitabilityFactorsStepProps & { histograms?: Record<string, DistrictHistogram> }>(
  ({ value, onChange, histograms }, ref) => {
    const { errors, selectionError, validate, clearWeightError } = useSuitabilityErrors(value);
    const { toggle, updateWeight } = useSuitabilitySelection(value, onChange, () => {});
    const selectedMap = useMemo(() => new Map(value.map((v) => [v.kind, v])), [value]);

    // New scoring rules state management
    function handleToggle(kind: string, checked: boolean) {
      toggle(kind, checked);
    }
    function handleUpdateWeight(kind: string, w: number | '') {
      updateWeight(kind, w, clearWeightError);
    }

    // New scoring rules data structure: breakpoints + points
    function getBreakpointsAndPoints(ranges: SuitabilityFactorRangeItem[]) {
      // Debug log
      // console.log('Getting breakpoints from ranges:', JSON.stringify(ranges));
      
      // Compatible with old data structure
      if (!ranges || ranges.length === 0) return { breakpoints: [], points: [] };
      
      // Handle null values that might occur from JSON serialization
      const validRanges = ranges.map(r => ({
        start: r.start === null ? -Infinity : r.start,
        end: r.end === null ? Infinity : r.end,
        points: r.points
      }));
      
      // Assume ranges are intervals, infer breakpoints automatically
      const sorted = [...validRanges].sort((a, b) => a.start - b.start);
      const breakpoints: number[] = [];
      for (let i = 0; i < sorted.length - 1; ++i) {
        if (Number.isFinite(sorted[i].end)) {
          breakpoints.push(sorted[i].end);
        }
      }
      const points = sorted.map(r => r.points);
      
      // Debug log
      // console.log('Resulting breakpoints:', breakpoints, 'points:', points);
      
      return { breakpoints, points };
    }
    function setBreakpointsAndPoints(kind: string, breakpoints: number[], points: number[]) {
      // Debug log
      // console.log('Setting breakpoints:', breakpoints, 'points:', points);
      
      // Generate ranges from breakpoints and points
      const sorted = [...breakpoints].sort((a, b) => a - b);
      const ranges: SuitabilityFactorRangeItem[] = [];
      let last = -Infinity;
      for (let i = 0; i < sorted.length; ++i) {
        ranges.push({ 
          start: last, 
          end: sorted[i], 
          points: Number.isFinite(points[i]) ? points[i] : NaN 
        });
        last = sorted[i];
      }
      ranges.push({ 
        start: last, 
        end: Infinity, 
        points: Number.isFinite(points[points.length - 1]) ? points[points.length - 1] : NaN 
      });
      
      // Debug log
      // console.log('Generated ranges:', JSON.stringify(ranges));
      
      // Update value
      const next = value.map(v => v.kind === kind ? { ...v, ranges } : v);
      onChange(next);
    }

    useImperativeHandle(ref, () => ({ validate }));

    return (
      <Stack spacing={2}>
        <FactorSelector selectionError={selectionError} />
        {ALL_FACTORS.map((opt) => {
          const selected = selectedMap.get(opt.code);
          const err = errors[opt.code];
          // Parse breakpoints/points
          const { breakpoints, points } = getBreakpointsAndPoints(selected?.ranges ?? []);
          function handleAddBreakpoint(v: number) {
            const newBreakpoints = [...breakpoints, v];
            // After adding a new breakpoint, insert a new points item, default to NaN
            const insertIdx = newBreakpoints.sort((a, b) => a - b).indexOf(v);
            const newPoints = [...points];
            newPoints.splice(insertIdx + 1, 0, NaN);
            setBreakpointsAndPoints(opt.code, newBreakpoints, newPoints);
          }
          function handleRemoveBreakpoint(idx: number) {
            const newBreakpoints = [...breakpoints];
            newBreakpoints.splice(idx, 1);
            const newPoints = [...points];
            // Merge intervals, remove the points at idx+1
            newPoints.splice(idx + 1, 1);
            setBreakpointsAndPoints(opt.code, newBreakpoints, newPoints);
          }
          function handlePointsChange(idx: number, v: number) {
            const newPoints = [...points];
            newPoints[idx] = v;
            setBreakpointsAndPoints(opt.code, breakpoints, newPoints);
          }
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
                  <FactorHistogram code={opt.code} histogram={histograms?.[opt.code]} />
                  <BreakpointScoringRules
                    breakpoints={breakpoints}
                    points={points}
                    onAddBreakpoint={handleAddBreakpoint}
                    onRemoveBreakpoint={handleRemoveBreakpoint}
                    onPointsChange={handlePointsChange}
                    error={err?.ranges ? { 
                      breakpoints: breakpoints.length === 0 ? 'At least one breakpoint is required' : undefined,
                      points: err.ranges.map(r => r.points || '') 
                    } : undefined}
                    minValue={histograms?.[opt.code]?.min ?? -Infinity}
                    maxValue={histograms?.[opt.code]?.max ?? Infinity}
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
  const { districtCode } = props;
  const { data, isLoading, error } = useQuery({
    queryKey: ['district-histograms', districtCode],
    queryFn: async () => {
      return await UserService.userGetDistrictHistograms({ districtCode });
    },
    enabled: !!districtCode,
    staleTime: 5 * 60 * 1000,
  });

  // Map histograms by kind for easy access
  const histograms: Record<string, DistrictHistogram> = useMemo(() => {
    if (!data || !('list' in data) || !data.list) return {};
    const map: Record<string, DistrictHistogram> = {};
    for (const item of data.list) {
      map[item.kind] = item.histogram;
    }
    return map;
  }, [data]);

  // Optionally, show loading or error states
  if (isLoading) return <Typography>Loading histograms...</Typography>;
  if (error) return <Typography color="error">Failed to load histograms</Typography>;

  return <SuitabilityFactorsStepInner {...props} ref={ref} histograms={histograms} />;
});

export default SuitabilityFactorsStep;
