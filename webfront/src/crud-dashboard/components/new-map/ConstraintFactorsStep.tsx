import { forwardRef, useImperativeHandle, useMemo, useState } from 'react';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormHelperText from '@mui/material/FormHelperText';

export interface ConstraintFactorsStepProps {
  textValue: string;
  onTextChange: (value: string) => void;
  selectValue: string;
  onSelectChange: (value: string) => void;
}

export type ConstraintFactorsStepHandle = { validate: () => boolean };

const ConstraintFactorsStep = forwardRef<ConstraintFactorsStepHandle, ConstraintFactorsStepProps>(
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

    const options = useMemo(() => ['Hard', 'Medium', 'Soft'], []);

    return (
      <Stack spacing={2}>
        <TextField
          required
          fullWidth
          label="Constraint factors"
          value={textValue}
          onChange={(e) => onTextChange(e.target.value)}
          error={Boolean(textError)}
          helperText={textError || 'Describe constraints to exclude areas.'}
        />

        <FormControl fullWidth error={Boolean(selectError)}>
          <InputLabel id="constraint-select-label">Constraint type</InputLabel>
          <Select
            labelId="constraint-select-label"
            label="Constraint type"
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

export default ConstraintFactorsStep;
