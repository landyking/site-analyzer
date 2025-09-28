import { forwardRef, useImperativeHandle } from 'react';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
// lists are rendered by shared components now
import type { ConstraintFactorsValue } from './ConstraintFactorsStep';
import type { SuitabilityFactorsValue } from './SuitabilityFactorsStep';
import ConstraintFactorsList from '../shared/ConstraintFactorsList';
import SuitabilityFactorsList from '../shared/SuitabilityFactorsList';

export interface ConfirmationData {
  name: string;
  district: string; // code
  districtLabel?: string;
  constraints: ConstraintFactorsValue;
  suitability: SuitabilityFactorsValue;
}

export interface ConfirmationStepProps {
  data: ConfirmationData;
}

export type ConfirmationStepHandle = { validate: () => boolean };

// Labels centralized in shared utils used by SuitabilityFactorsList

const ConfirmationStep = forwardRef<ConfirmationStepHandle, ConfirmationStepProps>(({ data }, ref) => {
  useImperativeHandle(ref, () => ({ validate: () => true }));

  const districtLabel = data.districtLabel || data.district;

  return (
    <Box sx={{ mb: 1 }}>
      <Box sx={{ p:2 ,pt: 0, bgcolor: 'background.paper', borderRadius: 1, }}>
        <Typography variant="h6" component="h2">
          Review & confirm
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This page shows a summary of the map you are about to create. Confirm the map name, chosen Territorial Authority,
          selected constraint factors (with distances) and suitability factors (weights & scoring rules). If everything looks
          correct, proceed to create the map.
        </Typography>
      </Box>
      <Box sx={{ px: 2, pt: 0 }}>
        <Stack spacing={2}>
          <Paper variant="outlined" sx={{ p: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
          Basics
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
            gap: 2,
          }}
        >
          <Box>
            <Typography>
              <strong>Map name:</strong> {data.name || '-'}
            </Typography>
          </Box>
          <Box>
            <Typography>
              <strong>Territorial Authority:</strong> {districtLabel || '-'}
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          gap: 2,
        }}
      >
        <Box>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
              Constraints
            </Typography>
            <ConstraintFactorsList items={data.constraints} />
          </Paper>
        </Box>

        <Box>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
              Suitability & weights
            </Typography>
            <SuitabilityFactorsList items={data.suitability} />
          </Paper>
        </Box>
      </Box>
        </Stack>
      </Box>
    </Box>
  );
});

export default ConfirmationStep;
