import React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import type { MapTaskFile, SuitabilityFactor } from '../../../../../client/types.gen';
import { SUITABILITY_LABELS, normalizeSuitabilityFactors, SuitabilityDisplayFactor } from '@/crud-dashboard/components/shared/suitability-utils';
import LeafletMap from '../../LeafletMap';
import Chip from '@mui/material/Chip';
import Avatar from '@mui/material/Avatar';
import Link from '@mui/material/Link';

// Solar farm suitability factors descriptions
const descriptionMap: Record<string, string> = {
  slope: 'Slope indicates the steepness of the terrain, which can affect construction and accessibility. Lower slopes are generally more suitable for solar farm installation.',
  powerlines: 'Powerline distances affects the cost and feasibility of connecting to the grid. Shorter distances generally reduce costs and improve feasibility.',
  roads: 'Road distances impact accessibility and transportation logistics for construction and maintenance. Shorter distances generally reduce costs and improve feasibility.',
  solar: 'Solar radiation levels are crucial for determining the potential energy output of solar panels. Higher radiation typically leads to better performance.',
  temperature: 'Temperature influences the efficiency and performance of solar panels. Moderate temperatures can make solar panels operate more efficiently.',
};

interface Props {
  factor: SuitabilityFactor;
  file: MapTaskFile | undefined;
}

const FactorCard: React.FC<Props> = ({ factor, file }) => {
  const title = SUITABILITY_LABELS[factor.kind] || factor.kind;
  const description = descriptionMap[factor.kind] || 'No description available.';
  const sf: SuitabilityDisplayFactor = normalizeSuitabilityFactors([factor] as unknown[])[0];
  const fileUrl = file?.file_path || '';
  return (
    <Paper id={`suitability-${factor.kind}`} variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Typography variant="subtitle1" sx={{ mb: 0 }}>{title} </Typography>
      <Box>
        <Box sx={{ mb: 1 }}>
          <Typography variant="body2" color="text.secondary">{description}</Typography>
          <Typography variant="subtitle2" sx={{ mt: 1,mb:-1 }}>Scoring Rules: </Typography>
          <Box sx={{ mt: 1 }}>
            {sf.ranges.map((r) => {
              let condition = '';
              const sFinite = Number.isFinite(r.start as number);
              const eFinite = Number.isFinite(r.end as number);
              if (sFinite && eFinite) {
                condition = `${r.start} ≤ value < ${r.end}`;
              } else if (sFinite) {
                condition = `value ≥ ${r.start}`;
              } else if (eFinite) {
                condition = `value < ${r.end}`;
              }
              return <Chip color="default" variant='outlined' size='small' avatar={<Avatar>{r.points}</Avatar>} label={condition} style={{marginRight: 2}}/>;
            })
            }
          </Box>
        </Box>
        <Box>
          <Typography variant="body2" sx={{ mt: 1 }} color="text.secondary">
            Darker map areas indicate higher scores according to the scoring rules.
            &nbsp;<Link href={fileUrl} target="_blank" rel="noopener" fontSize="small" color='text.secondary' download underline="none">Download</Link>
          </Typography>
          <LeafletMap fileUrl={file ? file.file_path : ''} fileTag={factor.kind} mapHeight={450} />
        </Box>
      </Box>
    </Paper>
  )
};

export default FactorCard;
