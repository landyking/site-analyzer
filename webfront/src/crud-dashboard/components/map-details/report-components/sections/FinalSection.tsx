import React from 'react';
import SectionPaper from '../SectionPaper';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Typography from '@mui/material/Typography';
import type { MapTaskDetails } from '../../../../../client/types.gen';
import LeafletMap from '../../LeafletMap';
import Link from '@mui/material/Link';
interface Props {
  mapTask: MapTaskDetails;
}
const FinalSection: React.FC<Props> = ({ mapTask }) => {
  const fileUrl = mapTask.files?.find(file => file.file_type == 'final')?.file_path || '';
  return (
    <SectionPaper id="final" title="Final result" icon={<CheckCircleIcon fontSize="small" color="primary" />}>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        The final map removes constrained areas from the weighted-overlay suitability layer, providing a clear visualization of locations suitable for solar farm development while respecting the defined constraints.
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 0 }}>
          Darker areas indicate higher overall suitability scores.
          &nbsp;<Link href={fileUrl} target="_blank" rel="noopener" fontSize="small" color='text.secondary' download underline="none">Download</Link>
        </Typography>
      <LeafletMap fileUrl={mapTask.files?.find(file => file.file_type == 'final')?.file_path || ''} fileTag="final" mapHeight={450} />
    </SectionPaper>
  )
};

export default FinalSection;
