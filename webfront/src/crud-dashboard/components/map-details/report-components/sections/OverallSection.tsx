import React from 'react';
import SectionPaper from '../SectionPaper';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Divider from '@mui/material/Divider';
import Button from '@mui/material/Button';

interface Props {
  mapTaskId?: number | string;
  suitabilityCount: number;
  restrictionsCount: number;
}

const OverallSection: React.FC<Props> = ({ mapTaskId, suitabilityCount, restrictionsCount }) => (
  <SectionPaper id="overall" title="Overall summary">
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 2 }}>
      <Box>
        <Typography variant="body2" color="text.secondary">
          This report summarizes the processing steps and outputs for task ID: {mapTaskId ?? 'N/A'}.
          It includes {suitabilityCount} suitability factors and {restrictionsCount} restricted factors.
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Button size="small" variant="outlined" href="#suitability">Jump to Suitability Scoring</Button>
        </Box>
      </Box>
      <Box>
        <Paper variant="outlined" sx={{ p: 1 }}>
          <Typography variant="subtitle2">Quick stats</Typography>
          <Divider sx={{ my: 1 }} />
          <Typography variant="body2">Suitability factors: {suitabilityCount}</Typography>
          <Typography variant="body2">Restricted factors: {restrictionsCount}</Typography>
        </Paper>
      </Box>
    </Box>
  </SectionPaper>
);

export default OverallSection;
