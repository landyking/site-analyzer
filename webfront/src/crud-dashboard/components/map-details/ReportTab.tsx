import React from 'react';
import Box from '@mui/material/Box';

// components moved to sections/* and imported below
import Outline from './report-components/sections/Outline';
import OverallSection from './report-components/sections/OverallSection';
import SuitabilitySection from './report-components/sections/SuitabilitySection';
import RestrictionsSection from './report-components/sections/RestrictionsSection';
import FinalSection from './report-components/sections/FinalSection';

interface ReportTabProps {
  // minimal props for now; will extend when implementing
  mapTaskId?: number | string;
}

const sampleSuitabilityFactors = [
  { key: 'slope', title: 'Slope', description: 'Slope in degrees. Lower is preferable.' },
  { key: 'distance_roads', title: 'Distance to roads', description: 'Distance to nearest road. Closer may be better for access.' },
  { key: 'land_cover', title: 'Land cover', description: 'Categorical land cover suitability scores.' },
];

const sampleRestrictedFactors = [
  { key: 'protected_areas', title: 'Protected areas' },
  { key: 'water_bodies', title: 'Water bodies' },
];

// components moved to ./report-components/

const ReportTab: React.FC<ReportTabProps> = ({ mapTaskId }) => {
  return (
    <Box sx={{ p: 2 }}>
      {/* Outline / Table of contents */}
      <Outline factors={sampleSuitabilityFactors} />
      <OverallSection mapTaskId={mapTaskId} suitabilityCount={sampleSuitabilityFactors.length} restrictionsCount={sampleRestrictedFactors.length} />
      <SuitabilitySection factors={sampleSuitabilityFactors} />
      <RestrictionsSection restrictions={sampleRestrictedFactors} />
      <FinalSection />
    </Box>
  );
};

export default ReportTab;
