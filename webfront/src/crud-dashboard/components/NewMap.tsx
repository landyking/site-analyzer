import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import PageContainer from './PageContainer';

export default function NewMap() {
  return (
    <PageContainer title="New Map" breadcrumbs={[{ title: 'New Map' }]}>
      <Box>
        <Typography color="text.secondary">
          Start creating a new map from data sources and layers.
        </Typography>
      </Box>
    </PageContainer>
  );
}
