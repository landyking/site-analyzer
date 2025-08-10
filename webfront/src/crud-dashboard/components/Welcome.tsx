// React import not required with react-jsx runtime
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PageContainer from './PageContainer';
import Button from '@mui/material/Button';
import { Link as RouterLink } from '@tanstack/react-router';

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
          to="/dashboard/my-maps"
        >
          Go to My Maps
        </Button>
      }
    >
      <Stack spacing={3} sx={{ maxWidth: 900 }}>
        <Typography variant="body1" color="text.secondary">
          Welcome to the Site Analyzer. Use the sidebar to create and manage map
          analysis tasks. Submit a new task with your district and factor weights,
          then monitor progress and download results when it’s done.
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
              • New Map: choose a district and set constraint/suitability factors to submit a task.
              <br />• My Maps: track status (Pending, Processing, Success, Failure, Cancelled) and access outputs.
              <br />• Use the header menu to collapse the sidebar on small screens.
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
              • Create a task in New Map, then watch it appear in My Maps.
              <br />• Check Tasks and Users if you have admin access.
              <br />• Return here anytime via the Welcome menu.
            </Typography>
          </Box>
        </Box>
      </Stack>
    </PageContainer>
  );
}
