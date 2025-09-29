import React from 'react';
import type { UserUserGetMapTaskResponse } from '../../../client/types.gen';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import TuneRoundedIcon from '@mui/icons-material/TuneRounded';
import StarRoundedIcon from '@mui/icons-material/StarRounded';
import Typography from '@mui/material/Typography';
import ConstraintFactorsList from '../shared/ConstraintFactorsList';
import SuitabilityFactorsList from '../shared/SuitabilityFactorsList';

interface InputFactorsTabProps {
  mapTask: NonNullable<UserUserGetMapTaskResponse['data']>;
}

const InputFactorsTab: React.FC<InputFactorsTabProps> = ({ mapTask }) => {
  const constraints = mapTask.constraint_factors || [];
  const suitability = mapTask.suitability_factors || [];

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
        gap: 2,
      }}
    >
      <Paper  sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <TuneRoundedIcon color="secondary" fontSize="small" />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Constraint Factors
          </Typography>
        </Box>
        <ConstraintFactorsList items={constraints} />
      </Paper>
      <Paper  sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <StarRoundedIcon color="secondary" fontSize="small" />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Suitability Factors
          </Typography>
        </Box>
        <SuitabilityFactorsList items={suitability} />
      </Paper>
    </Box>
  );
};

export default InputFactorsTab;