import React from 'react';
import SectionPaper from '../SectionPaper';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Divider from '@mui/material/Divider';
import Button from '@mui/material/Button';
import type { MapTaskDetails } from '../../../../../client/types.gen';

interface Props {
  mapTask: MapTaskDetails;
}

const OverallSection: React.FC<Props> = ({ mapTask }) => {
  const mapTaskId = mapTask.id;
  const suitabilityCount = mapTask.suitability_factors?.length || 0;
  const restrictionsCount = mapTask.constraint_factors?.length || 0;
  return (
    <SectionPaper id="overall" title="Overall summary">

      <Box>
        <Typography variant="body2" color="text.secondary">
          This report summarizes the processing steps and outputs for task ID: {mapTaskId ?? 'N/A'}.
          It includes {suitabilityCount} suitability factors and {restrictionsCount} restricted factors.
        </Typography>



      </Box>
    </SectionPaper>
  )
};

export default OverallSection;
