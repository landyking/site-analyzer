import React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';

interface Props {
  id?: string;
  title: string;
  icon?: React.ReactNode;
  children?: React.ReactNode;
}

const SectionPaper: React.FC<Props> = ({ id, title, icon, children }) => (
  <Paper id={id} variant="outlined" sx={{ p: 2, mb: 2 }}>
    <Typography variant="h6" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
      {icon ? <span style={{ display: 'inline-flex', alignItems: 'center' }}>{icon}</span> : null}
      <span>{title}</span>
    </Typography>
    {children}
  </Paper>
);

export default SectionPaper;
