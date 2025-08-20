import React from 'react';
import PageContainer from './PageContainer';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded';
import { useNavigate } from '@tanstack/react-router';

export default function MapDetails() {
  const navigate = useNavigate();
  const handleBack = () => {
    navigate({ to: '/dashboard/my-maps' });
  };
  const actions = (
    <IconButton aria-label="back" onClick={handleBack}>
      <ArrowBackRoundedIcon />
    </IconButton>
  );
  return (
    <PageContainer title="Map Details" actions={actions} breadcrumbs={[{ title: 'My Maps' }, { title: 'Map Details' }]}> 
      <Stack spacing={2}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Map Details
        </Typography>
        {/* Content will go here */}
      </Stack>
    </PageContainer>
  );
}
