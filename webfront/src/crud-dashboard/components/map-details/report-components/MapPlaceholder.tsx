import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

interface Props {
  caption?: string;
  height?: number | string;
}

const MapPlaceholder: React.FC<Props> = ({ caption, height = 220 }) => (
  <Box sx={{ position: 'relative' }}>
    <Box sx={{ border: '1px dashed', borderColor: 'divider', borderRadius: 1, height, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'background.paper' }}>
      <Typography color="text.secondary">Map placeholder</Typography>
    </Box>
    {caption && <Typography variant="caption" sx={{ position: 'absolute', bottom: 8, left: 8 }}>{caption}</Typography>}
  </Box>
);

export default MapPlaceholder;
