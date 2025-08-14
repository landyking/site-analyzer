import { forwardRef, useImperativeHandle, useMemo, useState } from 'react';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormHelperText from '@mui/material/FormHelperText';

export interface ConfirmationStepProps {
  textValue: string;
  onTextChange: (value: string) => void;
  selectValue: string;
  onSelectChange: (value: string) => void;
}

export type ConfirmationStepHandle = { validate: () => boolean };

const ConfirmationStep = forwardRef<ConfirmationStepHandle, ConfirmationStepProps>(
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

    const options = useMemo(() => ['Draft', 'Ready'], []);

    return (
      <Stack spacing={2}>
        <TextField
          required
          fullWidth
          label="Confirmation notes"
          value={textValue}
          onChange={(e) => onTextChange(e.target.value)}
          error={Boolean(textError)}
          helperText={textError || 'Any final notes before submission.'}
        />

        <FormControl fullWidth error={Boolean(selectError)}>
          <InputLabel id="confirmation-select-label">Status</InputLabel>
          <Select
            labelId="confirmation-select-label"
            label="Status"
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

export default ConfirmationStep;
