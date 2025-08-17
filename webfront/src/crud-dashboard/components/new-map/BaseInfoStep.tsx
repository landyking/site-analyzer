import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState } from 'react';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import type { SelectOptionItem } from '../../../client/types.gen';
import { UserService } from '../../../client/sdk.gen';

export type BaseInfoValue = { name: string; district: string };

export interface BaseInfoStepProps {
  value: BaseInfoValue;
  onChange: (value: BaseInfoValue) => void;
}

export type BaseInfoStepHandle = { validate: () => boolean };

const BaseInfoStep = forwardRef<BaseInfoStepHandle, BaseInfoStepProps>(
  ({ value, onChange }, ref) => {
    const [nameError, setNameError] = useState<string | undefined>();
    const [districtError, setDistrictError] = useState<string | undefined>();

    // Autocomplete state
    const [keyword, setKeyword] = useState('');
    const [options, setOptions] = useState<SelectOptionItem[]>([]);
    const [loading, setLoading] = useState(false);
    const debounceRef = useRef<number | undefined>(undefined);

    useImperativeHandle(ref, () => ({
      validate: () => {
        let ok = true;
  const t = value.name.trim();
        if (!t) {
          setNameError('Map name is required');
          ok = false;
        } else if (t.length > 20) {
          setNameError('Max length is 20');
          ok = false;
        } else {
          setNameError(undefined);
        }

  if (!value.district) {
          setDistrictError('Please select a Territorial Authority');
          ok = false;
        } else {
          setDistrictError(undefined);
        }
        return ok;
      },
    }));

    // Fetch district options with a small debounce on keyword changes
    useEffect(() => {
      window.clearTimeout(debounceRef.current);
      debounceRef.current = window.setTimeout(async () => {
        setLoading(true);
        try {
          const resp = await UserService.userGetDistrictSelectOptions({ limit: 50, keyword: keyword || undefined });
          setOptions(resp.list ?? []);
  } catch {
          // swallow; UI will just show no options
          setOptions([]);
        } finally {
          setLoading(false);
        }
      }, 300);
      return () => window.clearTimeout(debounceRef.current);
    }, [keyword]);

    return (
      <Stack spacing={2}>
        <TextField
          required
          fullWidth
          label="Map name"
          value={value.name}
          onChange={(e) => onChange({ ...value, name: e.target.value })}
          error={Boolean(nameError)}
          helperText={nameError || 'Up to 20 characters.'}
          inputProps={{ maxLength: 20 }}
        />

        <FormControl fullWidth error={Boolean(districtError)}>
          <Autocomplete
            options={options}
            loading={loading}
            getOptionLabel={(opt) => opt.label}
            isOptionEqualToValue={(a, b) => a.code === b.code}
            value={useMemo(() => options.find((o) => o.code === value.district) ?? null, [options, value.district])}
            onChange={(_, val) => {
              onChange({ ...value, district: val?.code ?? '' });
              setDistrictError(undefined);
            }}
            onInputChange={(_, val, reason) => {
              if (reason !== 'reset') setKeyword(val);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Territorial Authority"
                required
                error={Boolean(districtError)}
                helperText={districtError}
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
          {!districtError && <FormHelperText>Select a district by name.</FormHelperText>}
        </FormControl>
      </Stack>
    );
  },
);

export default BaseInfoStep;
