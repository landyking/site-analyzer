import React from 'react';
import SectionPaper from '../SectionPaper';
import PublicIcon from '@mui/icons-material/Public';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import type { MapTaskDetails } from '../../../../../client/types.gen';
import { SUITABILITY_LABELS } from '../../../shared/suitability-utils';
import { RESTRICTION_LABELS } from '../../../shared/constraint-utils';

interface Props {
  mapTask: MapTaskDetails;
}

const OverallSection: React.FC<Props> = ({ mapTask }) => {
  const mapTaskId = mapTask.id;
  const suitabilityCount = mapTask.suitability_factors?.length || 0;
  const restrictionsCount = mapTask.constraint_factors?.length || 0;

  const suitabilityNames = mapTask.suitability_factors?.map(f => SUITABILITY_LABELS[f.kind] || f.kind).join(', ') || '';
  const constraintNames = mapTask.constraint_factors?.map(f => RESTRICTION_LABELS[f.kind] || f.kind).join(', ') || '';

  const formatDuration = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    if (hours > 0) return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  const duration = mapTask.started_at && mapTask.ended_at && mapTask.status === 3
    ? formatDuration(new Date(mapTask.ended_at).getTime() - new Date(mapTask.started_at).getTime())
    : null;

  return (
    <SectionPaper id="overall" title="Overall summary" icon={<PublicIcon fontSize="small" color="primary" />}>

      <Box>
        <Typography variant="body2" color="text.secondary">
          Welcome to the site suitability analysis report for <Box component="span" sx={{ fontWeight: 'bold' }}>"{mapTask.name}"</Box> in <Box component="span" sx={{ fontWeight: 'bold' }}>{mapTask.district_name}</Box>.
          This report summarizes the processing steps and outputs for task ID: <Box component="span" sx={{ fontWeight: 'bold' }}>{mapTaskId ?? 'N/A'}</Box>.
          The analysis incorporates <Box component="span" sx={{ fontWeight: 'bold' }}>{suitabilityCount}</Box> suitability factors{suitabilityNames && ` (${suitabilityNames})`} and <Box component="span" sx={{ fontWeight: 'bold' }}>{restrictionsCount}</Box> constraint factors{constraintNames && ` (${constraintNames}) `}
          to help you identify optimal locations for your project.
          {duration && <> The task was completed in <Box component="span" sx={{ fontWeight: 'bold' }}>{duration}</Box>.</>}
        </Typography>
      </Box>
    </SectionPaper>
  )
};

export default OverallSection;
