import React from 'react';
import Box from '@mui/material/Box';

// components moved to sections/* and imported below
// import Outline from './report-components/sections/Outline';
import OverallSection from './report-components/sections/OverallSection';
import SuitabilitySection from './report-components/sections/SuitabilitySection';
import ConstraintsSection from './report-components/sections/ConstraintsSection';
import FinalSection from './report-components/sections/FinalSection';
import type { MapTaskDetails } from '../../../client/types.gen';

interface ReportTabProps {
  mapTask: MapTaskDetails;
}

// components moved to ./report-components/

const ReportTab: React.FC<ReportTabProps> = ({ mapTask }) => {
  return (
    <Box sx={{ p: 2 }}>
      {/* Outline / Table of contents */}
      {/* <Outline mapTask={mapTask} /> */}
      <OverallSection mapTask={mapTask} />
      <SuitabilitySection mapTask={mapTask} />
      <ConstraintsSection mapTask={mapTask} />
      <FinalSection mapTask={mapTask} />
    </Box>
  );
};

export default ReportTab;
