import React from 'react';
import SectionPaper from '../SectionPaper';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import Typography from '@mui/material/Typography';
import FactorCard from './FactorCard';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';
import type { MapTaskDetails } from '../../../../../client/types.gen';
import { SUITABILITY_LABELS } from '@/crud-dashboard/components/shared/suitability-utils';
import LeafletMap from '../../LeafletMap';

interface Props { mapTask: MapTaskDetails; }

const SuitabilitySection: React.FC<Props> = ({ mapTask }) => {
  const suitabilityFactors= mapTask.suitability_factors?.sort((a, b) => b.weight - a.weight) || [];
  return (
    <SectionPaper id="suitability" title="Suitability Scoring" icon={<TrendingUpIcon fontSize="small" color="primary" />}>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        The Suitability Scoring section breaks down each suitability factor into its own subsection with
        description, user-defined scoring rules, and a visualization of the corresponding layer.
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: 2 }}>
        {suitabilityFactors.map(f => (
          <FactorCard key={f.kind} factor={f} file={mapTask.files?.find(file => file.file_type == f.kind)} />
        ))}
      </Box>

      <SectionPaper title="Aggregated suitability (weighted sum)">
        <Typography variant="body2" color="text.secondary">This subsection shows how individual suitability factors are combined using weights to compute an aggregated suitability score.</Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2">Weights (example)</Typography>
          <List>
            {suitabilityFactors.map(f => (
              <ListItem key={f.kind} disablePadding>
                <ListItemText primary={`${SUITABILITY_LABELS[f.kind] || f.kind}: weight = 0.33 (placeholder)`} />
              </ListItem>
            ))}
          </List>
        </Box>
        <Box sx={{ mt: 0 }}>
          <LeafletMap fileUrl={mapTask.files?.find(file => file.file_type == 'weighted')?.file_path || ''} fileTag="weighted" mapHeight={450} />
        </Box>
      </SectionPaper>
    </SectionPaper>
  )
};

export default SuitabilitySection;
