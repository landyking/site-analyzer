import React from 'react';
import SectionPaper from '../SectionPaper';
import BlockIcon from '@mui/icons-material/Block';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import type { MapTaskDetails } from '../../../../../client/types.gen';
import LeafletMap from '../../LeafletMap';
import { CONSTRAINT_LABELS } from '@/crud-dashboard/components/shared/constraint-utils';
import Chip from '@mui/material/Chip';

interface Props { mapTask: MapTaskDetails; }

const ConstraintsSection: React.FC<Props> = ({ mapTask }) => (
  <SectionPaper id="constraints" title="Constraints" icon={<BlockIcon fontSize="small" color="primary" />}>
    <Typography variant="body2" color="text.secondary">
    The Constraints section integrates all user-defined constraint factors to identify forbidden zones (such as protected areas or wildlife habitats) where solar farm development is not permitted.
    </Typography>
    <Typography variant="subtitle2" sx={{ mt: 1,mb:0 }}>Constraint factors: </Typography>
    <Box sx={{ mb: 1 }}>
      {
        mapTask.constraint_factors?.map(r => (
          <Chip color="default" variant='outlined' size='small' label={`Distance from ${CONSTRAINT_LABELS[r.kind]} ≤ ${r.value} m`} style={{marginRight: 2}}/>
        ))}
    </Box>
    <Typography variant="body2" sx={{ mt: 1 }} color="text.secondary">Dark red map areas indicate forbidden zones.</Typography>
    <LeafletMap fileUrl={mapTask.files?.find(file => file.file_type == 'restricted')?.file_path || ''} fileTag="restricted" mapHeight={450} />
  </SectionPaper>
);

export default ConstraintsSection;
