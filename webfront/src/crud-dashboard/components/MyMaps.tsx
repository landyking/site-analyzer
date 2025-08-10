import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import PageContainer from './PageContainer';

export default function MyMaps() {
  return (
    <PageContainer title="My Maps" breadcrumbs={[{ title: 'My Maps' }]}>
      <Box>
        <Typography color="text.secondary">
          Browse and manage your saved maps here.
        </Typography>
      </Box>
    </PageContainer>
  );
}
