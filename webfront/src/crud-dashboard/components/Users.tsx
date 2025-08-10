import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import PageContainer from './PageContainer';

export default function Users() {
  return (
    <PageContainer title="Users" breadcrumbs={[{ title: 'Users' }]}>
      <Box>
        <Typography color="text.secondary">
          Manage users, roles, and access permissions.
        </Typography>
      </Box>
    </PageContainer>
  );
}
