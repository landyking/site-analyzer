import React from 'react';
import SectionPaper from '../SectionPaper';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import Typography from '@mui/material/Typography';
import FactorCard from './FactorCard';
import Box from '@mui/material/Box';
import type { MapTaskDetails } from '../../../../../client/types.gen';
import { SUITABILITY_LABELS } from '@/crud-dashboard/components/shared/suitability-utils';
import LeafletMap from '../../LeafletMap';
import Chip from '@mui/material/Chip';
import Avatar from '@mui/material/Avatar';
import Paper from '@mui/material/Paper';
import Link from '@mui/material/Link';

interface Props { mapTask: MapTaskDetails; }

const SuitabilitySection: React.FC<Props> = ({ mapTask }) => {
  const suitabilityFactors = mapTask.suitability_factors?.sort((a, b) => b.weight - a.weight) || [];
  const fileUrl = mapTask.files?.find(file => file.file_type == 'weighted')?.file_path || '';
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
      <Paper id={`suitability-weighted`} variant="outlined" sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" sx={{ mb: 0 }}>Weighted Overlay</Typography>

        <Box sx={{ mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            A weighted overlay map combines all individual suitability factors into a single comprehensive map,
            reflecting the overall suitability based on the assigned weights for each factor.
          </Typography>
          <Typography variant="subtitle2" sx={{ mt: 1, mb: -1 }}>Factor weights: </Typography>
          <Box sx={{ mt: 1 }}>
            {suitabilityFactors.map((f) => {
              const label = SUITABILITY_LABELS[f.kind] || f.kind;
              return <Chip color="default" variant='outlined' size='small' avatar={<Avatar>{f.weight}</Avatar>} label={label} style={{ marginRight: 2 }} />;
            })
            }
          </Box>
          <Box>
            <Typography variant="body2" sx={{ mt: 1 }} color="text.secondary">
              Darker areas indicate higher overall suitability scores based on the combined weighted factors.
              &nbsp;<Link href={fileUrl} target="_blank" rel="noopener" fontSize="small" color='text.secondary' download underline="none">Download</Link>
              </Typography>
            <LeafletMap fileUrl={mapTask.files?.find(file => file.file_type == 'weighted')?.file_path || ''} fileTag="weighted" mapHeight={450} />
          </Box>
        </Box>
      </Paper>
    </SectionPaper>
  )
};

export default SuitabilitySection;
