import { forwardRef, useImperativeHandle, useMemo, useState } from 'react';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormHelperText from '@mui/material/FormHelperText';

export interface SuitabilityFactorsStepProps {
  textValue: string;
  onTextChange: (value: string) => void;
  selectValue: string;
  onSelectChange: (value: string) => void;
}

export type SuitabilityFactorsStepHandle = { validate: () => boolean };

const SuitabilityFactorsStep = forwardRef<SuitabilityFactorsStepHandle, SuitabilityFactorsStepProps>(
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
        return ok;
      },
    }));

    const options = useMemo(() => ['High', 'Normal', 'Low'], []);

    return (
      <Stack spacing={2}>
        <TextField
          required
          fullWidth
          label="Suitability factors"
          value={textValue}
          onChange={(e) => onTextChange(e.target.value)}
          error={Boolean(textError)}
          helperText={textError || 'Describe suitability criteria for scoring.'}
        />

        <FormControl fullWidth error={Boolean(selectError)}>
          <InputLabel id="suitability-select-label">Priority</InputLabel>
          <Select
            labelId="suitability-select-label"
            label="Priority"
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

export default SuitabilityFactorsStep;
