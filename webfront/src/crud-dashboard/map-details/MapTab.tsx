import React from 'react';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';

const MapTab: React.FC = () => (
  <Box sx={{ p: 2 }}>
      <Alert severity="info" sx={{ background: '#eaf6fb', color: '#1976d2' }}>
        The map task status is pending / processing.
      </Alert>
    </Box>
);

export default MapTab;
