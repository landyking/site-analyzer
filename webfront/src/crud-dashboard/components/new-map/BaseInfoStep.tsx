import { forwardRef, useImperativeHandle, useMemo, useState } from 'react';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormHelperText from '@mui/material/FormHelperText';

export interface BaseInfoStepProps {
  textValue: string;
  onTextChange: (value: string) => void;
  selectValue: string;
  onSelectChange: (value: string) => void;
}

export type BaseInfoStepHandle = { validate: () => boolean };

const BaseInfoStep = forwardRef<BaseInfoStepHandle, BaseInfoStepProps>(
  ({ textValue, onTextChange, selectValue, onSelectChange }, ref) => {
    const [textError, setTextError] = useState<string | undefined>();
    const [selectError] = useState<string | undefined>(undefined);

    useImperativeHandle(ref, () => ({
      validate: () => {
        const t = textValue.trim();
        let ok = true;
        if (!t) {
          setTextError('This field is required');
          ok = false;
        } else {
          setTextError(undefined);
        }
        // Select is optional for now; adjust if needed
        return ok;
      },
    }));

    const options = useMemo(() => ['Option A', 'Option B', 'Option C'], []);

    return (
      <Stack spacing={2}>
        <TextField
          required
          fullWidth
          label="Map name"
          value={textValue}
          onChange={(e) => onTextChange(e.target.value)}
          error={Boolean(textError)}
          helperText={textError || 'Give your map a descriptive name.'}
        />

        <FormControl fullWidth error={Boolean(selectError)}>
          <InputLabel id="base-info-select-label">Sample option</InputLabel>
          <Select
            labelId="base-info-select-label"
            label="Sample option"
            value={selectValue}
            onChange={(e) => onSelectChange(String(e.target.value))}
          >
            {options.map((opt) => (
              <MenuItem key={opt} value={opt}>
                {opt}
              </MenuItem>
            ))}
          </Select>
          <FormHelperText>{selectError}</FormHelperText>
        </FormControl>
      </Stack>
    );
  },
);

export default BaseInfoStep;
