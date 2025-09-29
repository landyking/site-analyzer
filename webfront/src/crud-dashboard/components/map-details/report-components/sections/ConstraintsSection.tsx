import React from 'react';
import SectionPaper from '../SectionPaper';
import BlockIcon from '@mui/icons-material/Block';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';
import MapPlaceholder from '../MapPlaceholder';
import type { MapTaskDetails } from '../../../../../client/types.gen';
import LeafletMap from '../../LeafletMap';


const constraints = [
  { key: 'protected_areas', title: 'Protected areas' },
  { key: 'water_bodies', title: 'Water bodies' },
];

interface Props { mapTask: MapTaskDetails; }

const ConstraintsSection: React.FC<Props> = ({ mapTask }) => (
  <SectionPaper id="constraints" title="Constraints" icon={<BlockIcon fontSize="small" color="primary" />}>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      Constraint factors represent areas where development is not allowed or strongly discouraged. The following constrained layers are considered together.
    </Typography>
    <Box sx={{ mb: 2 }}>
      <List>
        {constraints.map(r => (
          <ListItem key={r.key} disablePadding>
            <ListItemText primary={r.title} />
          </ListItem>
        ))}
      </List>
    </Box>
    <LeafletMap fileUrl={mapTask.files?.find(file => file.file_type == 'restricted')?.file_path || ''} fileTag="restricted" mapHeight={450} />
  </SectionPaper>
);

export default ConstraintsSection;
