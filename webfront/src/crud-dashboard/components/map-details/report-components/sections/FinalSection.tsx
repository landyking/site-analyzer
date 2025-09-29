import React from 'react';
import SectionPaper from '../SectionPaper';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Typography from '@mui/material/Typography';
import MapPlaceholder from '../MapPlaceholder';
import type { MapTaskDetails } from '../../../../../client/types.gen';
import LeafletMap from '../../LeafletMap';
interface Props {
  mapTask: MapTaskDetails;
}
const FinalSection: React.FC<Props> = ({ mapTask }) => (
  <SectionPaper id="final" title="Final result" icon={<CheckCircleIcon fontSize="small" color="primary" />}>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      The final map applies the aggregated suitability map and excludes restricted areas. Different colours indicate suitability tiers (e.g., high/medium/low), or masked-out restricted areas.
    </Typography>
    <LeafletMap fileUrl={mapTask.files?.find(file => file.file_type == 'final')?.file_path || ''} fileTag="final" mapHeight={450} />
  </SectionPaper>
);

export default FinalSection;
