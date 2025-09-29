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
import TuneRoundedIcon from '@mui/icons-material/TuneRounded';
import StarRoundedIcon from '@mui/icons-material/StarRounded';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { useState } from 'react';
// import MapTab from './map-details/MapTab';
import ReportTab from './map-details/ReportTab';
import ProgressTab from './map-details/ProgressTab';
import FilesTab from './map-details/FilesTab';
import { useNavigate, useParams } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { UserService,AdminService } from '../../client/sdk.gen';
import ConstraintFactorsList from './shared/ConstraintFactorsList';
import SuitabilityFactorsList from './shared/SuitabilityFactorsList';



// Helper to format date/time
function formatDateTime(dt?: string) {
  if (!dt) return '-';
  const d = new Date(dt);
  if (isNaN(d.getTime())) return dt;
  return d.toLocaleString();
}


// Constraint list moved to shared component

// Suitability list moved to shared component



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

function MapTabs({ mapTask, isOngoing, admin }: { mapTask: NonNullable<UserUserGetMapTaskResponse['data']>; isOngoing: boolean; admin: boolean }) {
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
          <ProgressTab mapTask={mapTask} admin={admin} />
        </Box>
      </>
    );
  }

  // If files are missing/empty or status !== 3, show a tip instead of the Map tab
  const noMapToDisplay = !Array.isArray(mapTask.files) || mapTask.files.length === 0 || mapTask.status !== 3;

  // Tabs: Map, Report, Progress, Files (Files only if noMapToDisplay is false)
  const tabs = [
    { label: 'Report', show: true },
    { label: 'Progress', show: true },
    { label: 'Files', show: !noMapToDisplay },
  ];
  const visibleTabs = tabs.filter(t => t.show);

  return (
    <>
      <Tabs
        value={tabValue}
        onChange={(_, v) => setTabValue(v)}
        aria-label="Map details tabs"
        sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
      >
        {visibleTabs.map((tab) => (
          <Tab key={tab.label} label={tab.label} />
        ))}
      </Tabs>
      <Box sx={{ p: 0 }}>
        {/* Map Tab */}
        {tabValue === visibleTabs.findIndex(t => t.label === 'Report') && (
          noMapToDisplay ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No report is available to display yet. Please check the progress or try again later.
              </Typography>
            </Box>
          ) : (
            <ReportTab mapTask={mapTask} />
          )
        )}
        {/* Progress Tab */}
        {tabValue === visibleTabs.findIndex(t => t.label === 'Progress') && <ProgressTab mapTask={mapTask} admin={admin} />}
        {/* Files Tab */}
        {visibleTabs.some(t => t.label === 'Files') && tabValue === visibleTabs.findIndex(t => t.label === 'Files') && (
          <FilesTab mapTask={mapTask} />
        )}
      </Box>
    </>
  );
}

// Define types for the suitability factors

function MapSettings({ mapTask }: { mapTask: NonNullable<UserUserGetMapTaskResponse['data']> }) {
  const constraints = mapTask.constraint_factors || [];
  // Suitability factors displayed via shared component with internal normalization
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
  <ConstraintFactorsList items={constraints} />
      </Paper>
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <StarRoundedIcon color="secondary" fontSize="small" />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Suitability Factors
          </Typography>
        </Box>
  <SuitabilityFactorsList items={suitability} />
      </Paper>
    </Box>
  );
}

interface MapDetailsProps {
  admin: boolean;
}

const MapDetails: React.FC<MapDetailsProps> = ({ admin }) =>  {
  const navigate = useNavigate();
  const { taskId = '' } = useParams({ strict: false }) as { taskId?: string };
  const [polling, setPolling] = useState(false);
  const query = useQuery({
    queryKey: ['commonGetMapTask', taskId],
    queryFn: () => admin ? AdminService.adminGetMapTask({ taskId: Number(taskId) }) : UserService.userGetMapTask({ taskId: Number(taskId) }),
    enabled: !!taskId,
    refetchInterval: polling ? 10000 : false,
  });
  const { data, isLoading, isError, error } = query;

  const handleBack = () => {
    navigate({ to: admin ? '/dashboard/tasks' : '/dashboard/my-maps' });
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
  const parentTitle = admin ? 'Tasks' : 'My Maps';
  // If loading or error, show as before
  if (isLoading) {
    return (
      <PageContainer title="Details" actions={actions} breadcrumbs={[{ title: parentTitle }, { title: 'Details' }]}> 
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
      <PageContainer title="Details" actions={actions} breadcrumbs={[{ title: parentTitle }, { title: 'Details' }]}> 
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
      <PageContainer title="Details" actions={actions} breadcrumbs={[{ title: parentTitle }, { title: 'Details' }]}> 
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
      title="Details"
      actions={actions}
      breadcrumbs={[{ title: parentTitle }, { title: 'Details' }]}
    >
      <Stack spacing={3}>
        {/* Top summary info */}
        <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
          <MapSummary mapTask={mapTask} />
        </Paper>

        {/* Tabs for Map and Progress */}
        <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
          <MapTabs mapTask={mapTask} isOngoing={isOngoing} admin={admin} />
        </Paper>

        {/* Settings section */}
        <MapSettings mapTask={mapTask} />
      </Stack>
    </PageContainer>
  );
}
export function UserMapDetails(){
  return <MapDetails admin={false} />;
}
export function AdminMapDetails(){
  return <MapDetails admin={true} />;
}