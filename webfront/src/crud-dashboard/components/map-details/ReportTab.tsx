import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

interface ReportTabProps {
  // minimal props for now; will extend when implementing
  mapTaskId?: number | string;
}

const ReportTab: React.FC<ReportTabProps> = ({ mapTaskId }) => {
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6">Report view</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        This is a placeholder for the report-style view. It will list processing steps
        and render one map per step. Task ID: {mapTaskId ?? 'N/A'}
      </Typography>
    </Box>
  );
};

export default ReportTab;
