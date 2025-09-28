import React from 'react';
import SectionPaper from '../SectionPaper';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import Typography from '@mui/material/Typography';
import FactorCard from '../FactorCard';
import MapPlaceholder from '../MapPlaceholder';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';
import type { MapTaskDetails } from '../../../../../client/types.gen';

const factors = [
  { key: 'slope', title: 'Slope', description: 'Slope in degrees. Lower is preferable.' },
  { key: 'distance_roads', title: 'Distance to roads', description: 'Distance to nearest road. Closer may be better for access.' },
  { key: 'land_cover', title: 'Land cover', description: 'Categorical land cover suitability scores.' },
];

interface Props { mapTask: MapTaskDetails; }

const SuitabilitySection: React.FC<Props> = ({ mapTask }) => (
  <SectionPaper id="suitability" title="Suitability Scoring" icon={<TrendingUpIcon fontSize="small" color="primary" />}>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      The Suitability Scoring section breaks down each suitability factor into its own subsection with
      description, user-defined scoring rules, and a visualization of the corresponding layer.
    </Typography>

    {factors.map(f => (
      <FactorCard key={f.key} factor={f} />
    ))}

    <SectionPaper title="Aggregated suitability (weighted sum)">
      <Typography variant="body2" color="text.secondary">This subsection shows how individual suitability factors are combined using weights to compute an aggregated suitability score.</Typography>
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2">Weights (example)</Typography>
        <List>
          {factors.map(f => (
            <ListItem key={f.key} disablePadding>
              <ListItemText primary={`${f.title}: weight = 0.33 (placeholder)`} />
            </ListItem>
          ))}
        </List>
      </Box>
      <Box sx={{ mt: 2 }}>
        <MapPlaceholder caption="Aggregated suitability map" />
      </Box>
    </SectionPaper>
  </SectionPaper>
);

export default SuitabilitySection;
