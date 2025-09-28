import React from 'react';
import SectionPaper from '../SectionPaper';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';
import MapPlaceholder from '../MapPlaceholder';

interface Restrict { key: string; title: string }

interface Props { restrictions: Restrict[] }

const RestrictionsSection: React.FC<Props> = ({ restrictions }) => (
  <SectionPaper id="restrictions" title="Restrictions">
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      Restricted factors represent areas where development is not allowed or strongly discouraged. The following restricted layers are considered together.
    </Typography>
    <Box sx={{ mb: 2 }}>
      <List>
        {restrictions.map(r => (
          <ListItem key={r.key} disablePadding>
            <ListItemText primary={r.title} />
          </ListItem>
        ))}
      </List>
    </Box>
    <MapPlaceholder caption="Combined restrictions map" />
  </SectionPaper>
);

export default RestrictionsSection;
