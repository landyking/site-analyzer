import { forwardRef, useImperativeHandle } from 'react';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import type { ConstraintFactorsValue } from './ConstraintFactorsStep';
import type { SuitabilityFactorsValue } from './SuitabilityFactorsStep';

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

const SUITABILITY_LABELS: Record<string, string> = {
  solar: 'Annual solar radiation',
  temperature: 'Annual average temperature',
  roads: 'Road distances',
  powerlines: 'Powerline distances',
  slope: 'Land slope',
};

const ConfirmationStep = forwardRef<ConfirmationStepHandle, ConfirmationStepProps>(({ data }, ref) => {
  useImperativeHandle(ref, () => ({ validate: () => true }));

  const districtLabel = data.districtLabel || data.district;

  return (
    <Stack spacing={2}>
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
          Basic Info
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
              Constraint Factors
            </Typography>
            {data.constraints.length ? (
              <List dense>
                {data.constraints.map((cf) => {
                  const label = cf.label || cf.kind;
                  const text = `Distance from ${label}: ≥ ${Number.isFinite(cf.value) ? cf.value : 'x'} m`;
                  return (
                    <ListItem key={cf.kind} sx={{ py: 0 }}>
                      <ListItemText primary={text} />
                    </ListItem>
                  );
                })}
              </List>
            ) : (
              <Typography color="text.secondary">No constraint factors selected</Typography>
            )}
          </Paper>
        </Box>

        <Box>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
              Suitability Factors
            </Typography>
            {data.suitability.length ? (
              <List dense>
                {data.suitability.map((sf) => {
                  const label = SUITABILITY_LABELS[sf.kind] ?? sf.kind;
                  const header = `${label} – Weight: ${Number.isFinite(sf.weight) ? sf.weight : '0'}%`;
                  return (
                    <ListItem key={sf.kind} alignItems="flex-start" sx={{ display: 'block', py: 0 }}>
                      <Typography component="div">• {header}</Typography>
                      <List dense sx={{ pl: 3 }}>
                        {sf.ranges.map((r, idx) => (
                          <ListItem key={idx} sx={{ py: 0 }}>
                            <ListItemText
                              primary={`${Number.isFinite(r.start) ? r.start : 'x'}–${Number.isFinite(r.end) ? r.end : 'x'}: ${Number.isFinite(r.points) ? r.points : 'x'} points`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </ListItem>
                  );
                })}
              </List>
            ) : (
              <Typography color="text.secondary">No suitability factors selected</Typography>
            )}
          </Paper>
        </Box>
      </Box>
    </Stack>
  );
});

export default ConfirmationStep;
