import { forwardRef, useEffect, useImperativeHandle, useMemo, useState } from 'react';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import InputAdornment from '@mui/material/InputAdornment';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
// Divider removed; inputs are inline next to checkbox
import type { SelectOptionItem } from '../../../client/types.gen';
import { UserService } from '../../../client/sdk.gen';

export type ConstraintFactorItem = { kind: string; label?: string; value: number };
export type ConstraintFactorsValue = ConstraintFactorItem[];

export interface ConstraintFactorsStepProps {
  value: ConstraintFactorsValue;
  onChange: (value: ConstraintFactorsValue) => void;
}

export type ConstraintFactorsStepHandle = { validate: () => boolean };

const ConstraintFactorsStep = forwardRef<ConstraintFactorsStepHandle, ConstraintFactorsStepProps>(
  ({ value, onChange }, ref) => {
    const [errors, setErrors] = useState<Record<string, { value?: string }>>({});
  const [kindOptions, setKindOptions] = useState<SelectOptionItem[]>([]);
  const [kindsError, setKindsError] = useState<string | undefined>();

  const items = useMemo<ConstraintFactorsValue>(() => value, [value]);
  const selectedMap = useMemo(() => new Map(value.map((v) => [v.kind, v])), [value]);

    useImperativeHandle(ref, () => ({
      validate: () => {
        let ok = true;
        const nextErrors: Record<string, { value?: string }> = {};
        for (const it of items) {
          const ek: { value?: string } = {};
          if (!Number.isFinite(it.value)) {
            ek.value = 'Value is required and must be a number';
            ok = false;
          } else if (it.value <= 0) {
            ek.value = 'Value must be greater than 0';
            ok = false;
          } else if (it.value > 100000) {
            ek.value = 'Value must be less than or equal to 100000';
            ok = false;
          }
          if (ek.value) nextErrors[it.kind] = ek;
        }
        if (items.length === 0) {
          ok = false;
          setKindsError('Select at least one constraint factor');
        } else {
          setKindsError(undefined);
        }
        setErrors(nextErrors);
        return ok;
      },
    }));

    // Fetch all kind options once
    useEffect(() => {
      let ignore = false;
      (async () => {
        try {
          const resp = await UserService.userGetConstraintFactorsSelectOptions({ limit: 200 });
          if (!ignore) setKindOptions(resp.list ?? []);
        } catch {
          if (!ignore) setKindOptions([]);
        }
      })();
      return () => {
        ignore = true;
      };
    }, []);

  function updateItemByKind(kind: string, patch: Partial<ConstraintFactorItem>) {
      const base = [...value];
      const idx = base.findIndex((x) => x.kind === kind);
      if (idx >= 0) {
        base[idx] = { ...base[idx], ...patch } as ConstraintFactorItem;
        onChange(base);
      }
    }

  function toggle(kind: string, checked: boolean) {
      const idx = value.findIndex((v) => v.kind === kind);
      const next = [...value];
      if (checked && idx === -1) {
    const lbl = kindOptions.find((o) => o.code === kind)?.label;
    next.push({ kind, label: lbl, value: Number.NaN });
      } else if (!checked && idx >= 0) {
        next.splice(idx, 1);
      }
      onChange(next);
      setKindsError(undefined);
    }

    return (
      <Box sx={{ mb: 2 }}>
  <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1,  }}>
          <Typography variant="h6" component="h2">
            Constraint factors
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Select the constraint factors that should influence site suitability. For each selected
            factor, enter the required minimum distance (in meters). Values must be positive numbers
            — for example, enter how far a site must be from rivers, lakes, powerlines, or
            residential areas. These constraints will be used when excluding unsuitable sites during
            analysis.
          </Typography>
        </Box>
  <Box sx={{ p: 2, pt: 0,}}>
          <Stack spacing={2}>
        {/* Top-level helper/error for selection requirement */}
        <FormControl error={Boolean(kindsError)}>
          {kindsError ? (
            <FormHelperText>{kindsError}</FormHelperText>
          ) : null}
        </FormControl>

        {kindOptions.map((opt) => {
          const selected = selectedMap.get(opt.code);
          const err = selected ? errors[opt.code]?.value : undefined;
          return (
            <Paper key={opt.code} variant="outlined" sx={{ p: 2 }}>
              <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                <FormControlLabel
                  control={<Checkbox checked={Boolean(selected)} onChange={(_, c) => toggle(opt.code, c)} />}
                  label={<Typography variant="subtitle1">{opt.label}</Typography>}
                />

                {selected && (
                  <FormControl error={Boolean(err)} sx={{ minWidth: 280, maxWidth: 460 }}>
                    <TextField
                      required
                      type="number"
                      value={Number.isFinite(selected.value) ? selected.value : ''}
                      onChange={(e) => {
                        const v = e.target.value;
                        updateItemByKind(opt.code, { value: v === '' ? Number.NaN : Number(v), label: opt.label });
                        setErrors((prev) => ({ ...prev, [opt.code]: { value: undefined } }));
                      }}
                      error={Boolean(err)}
                      helperText={err}
                      inputProps={{ step: 'any', min: 1, max: 100000 }}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            {`Distance from ${opt.label} `}
                            {'>='}
                          </InputAdornment>
                        ),
                        endAdornment: <InputAdornment position="end">m</InputAdornment>,
                      }}
                    />
                  </FormControl>
                )}
              </Stack>
            </Paper>
          );
        })}
          </Stack>
        </Box>
      </Box>
    );
  },
);

export default ConstraintFactorsStep;
