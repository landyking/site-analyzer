// React import not required with react-jsx runtime
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { Link as RouterLink } from 'react-router';
import PageContainer from './PageContainer';

export default function Welcome() {
  return (
    <PageContainer
      title="Welcome"
      breadcrumbs={[{ title: 'Welcome' }]}
      actions={
        <Button
          variant="contained"
          color="primary"
          component={RouterLink}
          to="/employees"
        >
          Go to Employees
        </Button>
      }
    >
      <Stack spacing={3} sx={{ maxWidth: 900 }}>
        <Typography variant="body1" color="text.secondary">
          This dashboard is your starting point. Use the sidebar to navigate to
          different sections. The Employees area showcases a full CRUD flow with
          filters, sorting, pagination, and inline actions.
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
            }}
          >
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <LightbulbIcon color="warning" fontSize="small" />
              <Typography variant="subtitle2">Quick tips</Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">
              • Use the header menu button to collapse the sidebar on small screens.
              <br />• Bookmark specific pages; routing uses hash paths for easy linking.
            </Typography>
          </Box>
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
            }}
          >
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <CheckCircleIcon color="success" fontSize="small" />
              <Typography variant="subtitle2">What to try</Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">
              • View and edit employees, then return here via the Welcome menu.
              <br />• Explore nested items under Reports in the sidebar.
            </Typography>
          </Box>
        </Box>
      </Stack>
    </PageContainer>
  );
}
