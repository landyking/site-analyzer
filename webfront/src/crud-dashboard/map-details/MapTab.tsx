

import Box from '@mui/material/Box';
// import Alert from '@mui/material/Alert';
import type { MapTaskDetails } from '../../client/types.gen';

interface MapTabProps {
  mapTask?: MapTaskDetails | null;
}


const MapTab: React.FC<MapTabProps> = ({ mapTask }) => (
  <Box sx={{ p: 2 }}>
    {/* <Alert severity="info" sx={{ background: '#eaf6fb', color: '#1976d2', mb: 2 }}>
      The map task status is pending / processing.
    </Alert> */}
    <pre style={{ fontSize: 12, background: '#f5f5f5', padding: 12, borderRadius: 4, overflowX: 'auto' }}>
      {JSON.stringify(mapTask, null, 2)}
    </pre>
  </Box>
);

export default MapTab;
