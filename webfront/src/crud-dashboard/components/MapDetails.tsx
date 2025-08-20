import type { UserUserGetMapTaskResponse } from '../../client/types.gen';

// import React from 'react';
import PageContainer from './PageContainer';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Alert from '@mui/material/Alert';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import SettingsRoundedIcon from '@mui/icons-material/SettingsRounded';
import TuneRoundedIcon from '@mui/icons-material/TuneRounded';
import StarRoundedIcon from '@mui/icons-material/StarRounded';
import { useNavigate, useParams } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { UserService } from '../../client/sdk.gen';

// Reuse labels from ConfirmationStep
const SUITABILITY_LABELS: Record<string, string> = {
  solar: 'Annual solar radiation',
  temperature: 'Annual average temperature',
  roads: 'Road distances',
  powerlines: 'Powerline distances',
  slope: 'Land slope',
};


// Helper to format date/time
function formatDateTime(dt?: string) {
  if (!dt) return '-';
  const d = new Date(dt);
  if (isNaN(d.getTime())) return dt;
  return d.toLocaleString();
}


function ConstraintList({ constraints }: { constraints: { kind: string; label?: string; value?: number }[] }) {
  return constraints.length ? (
    <List dense>
      {constraints.map((cf) => {
        const label = cf.label || cf.kind;
        const text = `Distance from ${label}: ≥ ${Number.isFinite(cf.value) ? cf.value : 'x'} m`;
        return (
          <ListItem key={cf.kind} sx={{ py: 0 }}>
            <ListItemText primary={text} />
          </ListItem>
        );
      })}
    </List>
  ) : (
    <Typography color="text.secondary">No constraint factors selected</Typography>
  );
}

function SuitabilityList({ suitability }: { suitability: { kind: string; weight: number; ranges: { start: number; end: number; points: number }[] }[] }) {
  return suitability.length ? (
    <List dense>
      {suitability.map((sf) => {
        const label = SUITABILITY_LABELS[sf.kind] ?? sf.kind;
        const header = `${label} – Weight: ${Number.isFinite(sf.weight) ? sf.weight : '0'}%`;
        return (
          <ListItem key={sf.kind} alignItems="flex-start" sx={{ display: 'block', py: 0 }}>
            <Typography component="div" sx={{ fontWeight: 500, mb: 0.5, color: 'primary.main' }}>
              • {header}
            </Typography>
            <List dense sx={{ pl: 3 }}>
              {sf.ranges.map((r, idx) => (
                <ListItem key={idx} sx={{ py: 0 }}>
                  <ListItemText
                    primary={`${Number.isFinite(r.start) ? r.start : 'x'}–${Number.isFinite(r.end) ? r.end : 'x'}: ${Number.isFinite(r.points) ? r.points : 'x'} points`}
                  />
                </ListItem>
              ))}
            </List>
          </ListItem>
        );
      })}
    </List>
  ) : (
    <Typography color="text.secondary">No suitability factors selected</Typography>
  );
}


export default function MapDetails() {
  const navigate = useNavigate();
  const { taskId = '' } = useParams({ strict: false }) as { taskId?: string };


  const query = useQuery({
    queryKey: ['userGetMapTask', taskId],
    queryFn: () => UserService.userGetMapTask({ taskId: Number(taskId) }),
    enabled: !!taskId,
  });
  const { data, isLoading, isError, error } = query;

  const handleBack = () => {
    navigate({ to: '/dashboard/my-maps' });
  };
  const actions = (
    <IconButton aria-label="back" onClick={handleBack}>
      <ArrowBackRoundedIcon />
    </IconButton>
  );

  // Use the generated API response type
  let mapTask: UserUserGetMapTaskResponse['data'] | undefined = undefined;
  if (data && typeof data === 'object' && 'data' in data) {
    mapTask = (data as UserUserGetMapTaskResponse).data;
  }

  const summary = {
    name: mapTask?.name || '-',
    district: mapTask?.district_name || '-',
    createdAt: formatDateTime(mapTask?.created_at ?? undefined),
    startedAt: formatDateTime(mapTask?.started_at ?? undefined),
    endedAt: formatDateTime(mapTask?.ended_at ?? undefined),
    status: mapTask?.status_desc,
  };
  const constraints = mapTask?.constraint_factors || [];
  const suitability = mapTask?.suitability_factors || [];

  return (
    <PageContainer
      title="Map Details"
      actions={actions}
      breadcrumbs={[{ title: 'My Maps' }, { title: 'Map Details' }]}
    >
      <Stack spacing={3}>
        {/* Top summary info */}
        <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
          {isLoading ? (
            <Typography>Loading...</Typography>
          ) : isError ? (
            <Alert severity="error">{(error instanceof Error ? error.message : 'Failed to load map task.')}</Alert>
          ) : (
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' },
                gap: 2,
                alignItems: 'center',
              }}
            >
              <Box>
                <Typography>
                  <strong>Name:</strong> {summary.name}
                </Typography>
                <Typography>
                  <strong>Created At:</strong> {summary.createdAt}
                </Typography>
              </Box>
              <Box>
                <Typography>
                  <strong>District:</strong> {summary.district}
                </Typography>
                <Typography>
                  <strong>Started At:</strong> {summary.startedAt}
                </Typography>
              </Box>
              <Box>
                <Typography>
                  <strong>Status:</strong> {summary.status}
                </Typography>
                <Typography>
                  <strong>Ended At:</strong> {summary.endedAt}
                </Typography>
              </Box>
            </Box>
          )}
        </Paper>

        {/* Map section (unchanged) */}
        <Paper variant="outlined" sx={{ p: 0, mb: 1 }}>
          <Box sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider', background: '#f5f7fa', display: 'flex', alignItems: 'center', gap: 1 }}>
            <StarRoundedIcon color="primary" fontSize="small" />
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              Map
            </Typography>
          </Box>
          <Box sx={{ p: 2 }}>
            <Alert severity="info" sx={{ background: '#eaf6fb', color: '#1976d2' }}>
              The map task status is pending / processing.
            </Alert>
          </Box>
        </Paper>

        {/* Settings section */}
        {/* <Paper variant="outlined" sx={{ p: 0 }}> */}
          {/* <Box sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider', background: 'linear-gradient(90deg, #f5f7fa 0%, #e3eafc 100%)', display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsRoundedIcon color="primary" fontSize="small" />
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              Settings
            </Typography>
          </Box> */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
              gap: 2,
              // p: 2,
            }}
          >
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <TuneRoundedIcon color="secondary" fontSize="small" />
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Constraint Factors
                </Typography>
              </Box>
              {isLoading ? (
                <Typography color="text.secondary">Loading...</Typography>
              ) : isError ? (
                <Typography color="error">Failed to load.</Typography>
              ) : (
                <ConstraintList constraints={constraints} />
              )}
            </Paper>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <StarRoundedIcon color="secondary" fontSize="small" />
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Suitability Factors
                </Typography>
              </Box>
              {isLoading ? (
                <Typography color="text.secondary">Loading...</Typography>
              ) : isError ? (
                <Typography color="error">Failed to load.</Typography>
              ) : (
                <SuitabilityList suitability={suitability} />
              )}
            </Paper>
          </Box>
        {/* </Paper> */}
      </Stack>
    </PageContainer>
  );
}
