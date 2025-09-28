import React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';

interface Props {
  id?: string;
  title: string;
  children?: React.ReactNode;
}

const SectionPaper: React.FC<Props> = ({ id, title, children }) => (
  <Paper id={id} variant="outlined" sx={{ p: 2, mb: 2 }}>
    <Typography variant="h6" sx={{ mb: 1 }}>{title}</Typography>
    {children}
  </Paper>
);

export default SectionPaper;
