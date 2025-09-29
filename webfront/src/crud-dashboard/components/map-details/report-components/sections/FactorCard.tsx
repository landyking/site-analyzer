import React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import MapPlaceholder from '../MapPlaceholder';
import type { SuitabilityFactor } from '../../../../../client/types.gen';
import { SUITABILITY_LABELS } from '@/crud-dashboard/components/shared/suitability-utils';

interface Props {
  factor: SuitabilityFactor;
}

const FactorCard: React.FC<Props> = ({ factor }) => {
  const title = SUITABILITY_LABELS[factor.kind] || factor.kind;
  const description= '';
  return (
    <Paper id={`suitability-${factor.kind}`} variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Typography variant="subtitle1" sx={{ mb: 1 }}>{title}</Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '7fr 5fr' }, gap: 2 }}>
        <Box>
          <Typography variant="body2" color="text.secondary">{description}</Typography>
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption">User-defined scoring rules (placeholder)</Typography>
            <Typography variant="body2" sx={{ mt: 1 }} color="text.secondary">{"e.g. slope < 5 -> score 1.0; slope 5-15 -> 0.5; >15 -> 0.0"}</Typography>
          </Box>
        </Box>
        <Box>
          <MapPlaceholder caption={title} />
        </Box>
      </Box>
    </Paper>
  )
};

export default FactorCard;
