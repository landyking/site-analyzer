import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState } from 'react';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import InputAdornment from '@mui/material/InputAdornment';
import type { SelectOptionItem } from '../../../client/types.gen';
import { UserService } from '../../../client/sdk.gen';

export type ConstraintFactorItem = { kind: string; value: number };
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
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState('');
  const debounceRef = useRef<number | undefined>(undefined);
  const [kindsError, setKindsError] = useState<string | undefined>();

    const items = useMemo<ConstraintFactorsValue>(() => value, [value]);

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

    // Fetch kind options (debounced by keyword)
    useEffect(() => {
      window.clearTimeout(debounceRef.current);
      debounceRef.current = window.setTimeout(async () => {
        setLoading(true);
        try {
          const resp = await UserService.userGetConstraintFactorsSelectOptions({ limit: 50, keyword: keyword || undefined });
          setKindOptions(resp.list ?? []);
        } catch {
          setKindOptions([]);
        } finally {
          setLoading(false);
        }
      }, 300);
      return () => window.clearTimeout(debounceRef.current);
    }, [keyword]);

    function updateItemByKind(kind: string, patch: Partial<ConstraintFactorItem>) {
      const base = [...value];
      const idx = base.findIndex((x) => x.kind === kind);
      if (idx >= 0) {
        base[idx] = { ...base[idx], ...patch } as ConstraintFactorItem;
        onChange(base);
      }
    }

    return (
      <Stack spacing={2}>
    <FormControl fullWidth error={Boolean(kindsError)}>
          <Autocomplete
            multiple
            options={kindOptions}
            loading={loading}
            getOptionLabel={(opt) => opt.label}
            isOptionEqualToValue={(a, b) => a.code === b.code}
            value={kindOptions.filter((o) => value.some((v) => v.kind === o.code))}
            onChange={(_, sel) => {
              const selectedCodes = sel.map((s) => s.code);
              const next: ConstraintFactorsValue = [];
              // keep existing values for selected kinds
              for (const code of selectedCodes) {
                const existing = value.find((v) => v.kind === code);
                next.push({ kind: code, value: existing?.value ?? Number.NaN });
              }
              onChange(next);
      setKindsError(undefined);
            }}
            onInputChange={(_, val, reason) => {
              if (reason !== 'reset') setKeyword(val);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Constraint factors"
                placeholder="Select one or more constraint factors"
        error={Boolean(kindsError)}
        helperText={kindsError}
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {loading ? <CircularProgress color="inherit" size={18} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
              />
            )}
          />
          {!kindsError && (
            <FormHelperText>
              Select constraint factors; each will require a distance value.
            </FormHelperText>
          )}
        </FormControl>

        {items.map((it) => {
          const opt = kindOptions.find((o) => o.code === it.kind);
          const label = opt?.label ?? it.kind;
          const err = errors[it.kind]?.value;
          return (
            <FormControl key={it.kind} fullWidth error={Boolean(err)}>
              <TextField
                required
                type="number"
                value={Number.isFinite(it.value) ? it.value : ''}
                onChange={(e) => {
                  const v = e.target.value;
                  updateItemByKind(it.kind, { value: v === '' ? Number.NaN : Number(v) });
                  setErrors((prev) => ({ ...prev, [it.kind]: { value: undefined } }));
                }}
                error={Boolean(err)}
                helperText={err}
                  inputProps={{ step: 'any', min: 0 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      {`Distance from ${label} `}{'>='}
                    </InputAdornment>
                  ),
                  endAdornment: <InputAdornment position="end">m</InputAdornment>,
                }}
              />
            </FormControl>
          );
        })}
      </Stack>
    );
  },
);

export default ConstraintFactorsStep;
