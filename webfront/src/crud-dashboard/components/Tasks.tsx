import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import PageContainer from './PageContainer';

export default function Tasks() {
  return (
    <PageContainer title="Tasks" breadcrumbs={[{ title: 'Tasks' }]}>
      <Box>
        <Typography color="text.secondary">
          Track and manage background processing tasks.
        </Typography>
      </Box>
    </PageContainer>
  );
}
