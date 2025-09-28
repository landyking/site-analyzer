import React from 'react';
import SectionPaper from '../SectionPaper';
import Typography from '@mui/material/Typography';
import MapPlaceholder from '../MapPlaceholder';
import type { MapTaskDetails } from '../../../../../client/types.gen';
interface Props {
  mapTask: MapTaskDetails;
}
const FinalSection: React.FC<Props> = ({ mapTask }) => (
  <SectionPaper id="final" title="Final result">
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      The final map applies the aggregated suitability map and excludes restricted areas. Different colours indicate suitability tiers (e.g., high/medium/low), or masked-out restricted areas.
    </Typography>
    <MapPlaceholder caption="Final suitability map (aggregated & masked)" />
  </SectionPaper>
);

export default FinalSection;
