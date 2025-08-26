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
import TuneRoundedIcon from '@mui/icons-material/TuneRounded';
import StarRoundedIcon from '@mui/icons-material/StarRounded';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { useState } from 'react';
import MapTab from './map-details/MapTab';
import ProgressTab from './map-details/ProgressTab';
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



// --- Subcomponents ---
function MapSummary({ mapTask }: { mapTask: NonNullable<UserUserGetMapTaskResponse['data']> }) {
  const summary = {
    name: mapTask.name || '-',
    district: mapTask.district_name || '-',
    createdAt: formatDateTime(mapTask.created_at),
    startedAt: formatDateTime(mapTask.started_at ?? undefined),
    endedAt: formatDateTime(mapTask.ended_at ?? undefined),
    status: mapTask.status_desc,
  };
  return (
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
  );
}

function MapTabs({ mapTask, isOngoing }: { mapTask: NonNullable<UserUserGetMapTaskResponse['data']>; isOngoing: boolean }) {
  const [tabValue, setTabValue] = useState(0);
  if (isOngoing) {
    return (
      <>
        <Tabs
          value={0}
          aria-label="Map details tabs"
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab label="Progress" />
        </Tabs>
        <Box sx={{ p: 0 }}>
          <ProgressTab mapTask={mapTask} />
        </Box>
      </>
    );
  }

  // If files are missing/empty or status !== 3, show a tip instead of the Map tab
  const noMapToDisplay = !Array.isArray(mapTask.files) || mapTask.files.length === 0 || mapTask.status !== 3;

  return (
    <>
      <Tabs
        value={tabValue}
        onChange={(_, v) => setTabValue(v)}
        aria-label="Map details tabs"
        sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
      >
        <Tab label="Map" />
        <Tab label="Progress" />
      </Tabs>
      <Box sx={{ p: 0 }}>
        {tabValue === 0 && (
          noMapToDisplay ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No map is available to display yet. Please check the progress or try again later.
              </Typography>
            </Box>
          ) : (
            <MapTab mapTask={mapTask} />
          )
        )}
        {tabValue === 1 && <ProgressTab mapTask={mapTask} />}
      </Box>
    </>
  );
}

function MapSettings({ mapTask }: { mapTask: NonNullable<UserUserGetMapTaskResponse['data']> }) {
  const constraints = mapTask.constraint_factors || [];
  const suitability = mapTask.suitability_factors || [];
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
        gap: 2,
      }}
    >
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <TuneRoundedIcon color="secondary" fontSize="small" />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Constraint Factors
          </Typography>
        </Box>
        <ConstraintList constraints={constraints} />
      </Paper>
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <StarRoundedIcon color="secondary" fontSize="small" />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Suitability Factors
          </Typography>
        </Box>
        <SuitabilityList suitability={suitability} />
      </Paper>
    </Box>
  );
}

export default function MapDetails() {
  const navigate = useNavigate();
  const { taskId = '' } = useParams({ strict: false }) as { taskId?: string };
  const [polling, setPolling] = useState(false);
  const query = useQuery({
    queryKey: ['userGetMapTask', taskId],
    queryFn: () => UserService.userGetMapTask({ taskId: Number(taskId) }),
    enabled: !!taskId,
    refetchInterval: polling ? 10000 : false,
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

  let mapTask: UserUserGetMapTaskResponse['data'] | undefined = undefined;
  if (data && typeof data === 'object' && 'data' in data) {
    mapTask = (data as UserUserGetMapTaskResponse).data;
  }

  // If loading or error, show as before
  if (isLoading) {
    return (
      <PageContainer title="Map Details" actions={actions} breadcrumbs={[{ title: 'My Maps' }, { title: 'Map Details' }]}> 
        <Stack spacing={3}>
          <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
            <Typography>Loading...</Typography>
          </Paper>
        </Stack>
      </PageContainer>
    );
  }
  if (isError) {
    return (
      <PageContainer title="Map Details" actions={actions} breadcrumbs={[{ title: 'My Maps' }, { title: 'Map Details' }]}> 
        <Stack spacing={3}>
          <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
            <Alert severity="error">{(error instanceof Error ? error.message : 'Failed to load map task.')}</Alert>
          </Paper>
        </Stack>
      </PageContainer>
    );
  }

  // If mapTask is null or undefined, show error
  if (!mapTask) {
    return (
      <PageContainer title="Map Details" actions={actions} breadcrumbs={[{ title: 'My Maps' }, { title: 'Map Details' }]}> 
        <Stack spacing={3}>
          <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
            <Alert severity="error">Map task not found or invalid.</Alert>
          </Paper>
        </Stack>
      </PageContainer>
    );
  }

  // Determine if task is ongoing (status < 3)
  const isOngoing = typeof mapTask.status === 'number' && mapTask.status < 3;
  if (polling !== !!isOngoing) {
    setPolling(!!isOngoing);
  }

  return (
    <PageContainer
      title="Map Details"
      actions={actions}
      breadcrumbs={[{ title: 'My Maps' }, { title: 'Map Details' }]}
    >
      <Stack spacing={3}>
        {/* Top summary info */}
        <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
          <MapSummary mapTask={mapTask} />
        </Paper>

        {/* Tabs for Map and Progress */}
        <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
          <MapTabs mapTask={mapTask} isOngoing={isOngoing} />
        </Paper>

        {/* Settings section */}
        <MapSettings mapTask={mapTask} />
      </Stack>
    </PageContainer>
  );
}
