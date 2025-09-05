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
import TuneRoundedIcon from '@mui/icons-material/TuneRounded';
import StarRoundedIcon from '@mui/icons-material/StarRounded';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { useState } from 'react';
import MapTab from './map-details/MapTab';
import ProgressTab from './map-details/ProgressTab';
import FilesTab from './map-details/FilesTab';
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
        return (
          <ListItem key={cf.kind} sx={{ py: 0.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography 
                component="span" 
                sx={{ 
                  fontSize: '0.875rem', 
                  fontWeight: 500,
                  color: 'text.secondary',
                  bgcolor: 'action.hover',
                  borderRadius: 1,
                  px: 1,
                  py: 0.2,
                  mr: 1
                }}
              >
                Distance from {label}
              </Typography>
              <Typography 
                component="span" 
                sx={{ 
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: 'success.main' 
                }}
              >
                ≥ {Number.isFinite(cf.value) ? `${cf.value} m` : 'x m'}
              </Typography>
            </Box>
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
        const header = `${label} – Weight: ${Number.isFinite(sf.weight) ? sf.weight : '0'}`;
        return (
          <ListItem key={sf.kind} alignItems="flex-start" sx={{ display: 'block', py: 0 }}>
            <Typography component="div" sx={{ fontWeight: 500, mb: 0.5, color: 'secondary.main' }}>
              • {header}
            </Typography>
            <List dense sx={{ pl: 3 }}>
              {sf.ranges.map((r, idx) => {
                // Format the range as a condition using comparison operators
                let condition = '';
                if (Number.isFinite(r.start) && Number.isFinite(r.end)) {
                  // Both start and end are finite - show as a range
                  condition = `${r.start} ≤ value < ${r.end}`;
                } else if (Number.isFinite(r.start)) {
                  // Only start is finite - show as greater than or equal
                  condition = `value ≥ ${r.start}`;
                } else if (Number.isFinite(r.end)) {
                  // Only end is finite - show as less than
                  condition = `value < ${r.end}`;
                }
                // If both are non-finite, we would have an empty condition
                
                return (
                  <ListItem key={idx} sx={{ py: 0.5 }}>
                    {condition ? (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography 
                          component="span" 
                          sx={{ 
                            fontSize: '0.875rem', 
                            fontWeight: 500,
                            color: 'text.secondary',
                            bgcolor: 'action.hover',
                            borderRadius: 1,
                            px: 1,
                            py: 0.2,
                            mr: 1
                          }}
                        >
                          {condition}
                        </Typography>
                        <Typography 
                          component="span" 
                          sx={{ 
                            fontSize: '0.875rem',
                            fontWeight: 600,
                            color: 'success.main' 
                          }}
                        >
                          {Number.isFinite(r.points) ? `${r.points} points` : 'x points'}
                        </Typography>
                      </Box>
                    ) : (
                      <Typography sx={{ color: 'success.main', fontWeight: 500 }}>
                        {Number.isFinite(r.points) ? `${r.points} points` : 'x points'}
                      </Typography>
                    )}
                  </ListItem>
                );
              })}
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

  // Tabs: Map, Progress, Files (Files only if noMapToDisplay is false)
  const tabs = [
    { label: 'Map', show: true },
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
        {tabValue === visibleTabs.findIndex(t => t.label === 'Map') && (
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
        {/* Progress Tab */}
        {tabValue === visibleTabs.findIndex(t => t.label === 'Progress') && <ProgressTab mapTask={mapTask} />}
        {/* Files Tab */}
        {visibleTabs.some(t => t.label === 'Files') && tabValue === visibleTabs.findIndex(t => t.label === 'Files') && (
          <FilesTab mapTask={mapTask} />
        )}
      </Box>
    </>
  );
}

// Define types for the suitability factors
type NewSuitabilityFactor = {
  kind: string;
  weight: number;
  ranges?: Array<{ start: number; end: number; points: number }>;
  breakpoints?: number[];
  points?: number[];
};

type OldSuitabilityFactor = {
  kind: string;
  weight: number;
  ranges: Array<{ start: number; end: number; points: number }>;
};

// Convert new suitability factor format to old format
function convertToOldSuitabilityFormat(suitabilityFactors: NewSuitabilityFactor[]): OldSuitabilityFactor[] {
  if (!suitabilityFactors || !Array.isArray(suitabilityFactors)) return [];
  
  return suitabilityFactors.map(factor => {
    // If already has ranges, return as-is with proper type
    if (factor.ranges && Array.isArray(factor.ranges) && factor.ranges.length > 0) {
      return {
        kind: factor.kind,
        weight: factor.weight,
        ranges: factor.ranges
      };
    }
    
    // Convert from new breakpoints/points format to old ranges format
    const { breakpoints, points, kind, weight } = factor;
    
    // If no breakpoints or points, return minimal structure
    if (!Array.isArray(breakpoints) || !Array.isArray(points) || breakpoints.length === 0) {
      return { kind, weight, ranges: [] };
    }
    
    // Sort breakpoints to ensure correct order
    const sortedBreakpoints = [...breakpoints].sort((a, b) => a - b);
    
    // Create ranges from breakpoints and points
    const ranges: Array<{ start: number; end: number; points: number }> = [];
    let lastPoint = -Infinity;
    
    // Create ranges for each interval
    for (let i = 0; i < sortedBreakpoints.length; i++) {
      ranges.push({
        start: lastPoint,
        end: sortedBreakpoints[i],
        points: Number.isFinite(points[i]) ? points[i] : NaN
      });
      lastPoint = sortedBreakpoints[i];
    }
    
    // Add the final range (after the last breakpoint)
    ranges.push({
      start: lastPoint,
      end: Infinity,
      points: Number.isFinite(points[points.length - 1]) ? points[points.length - 1] : NaN
    });
    
    return { kind, weight, ranges };
  });
}

function MapSettings({ mapTask }: { mapTask: NonNullable<UserUserGetMapTaskResponse['data']> }) {
  const constraints = mapTask.constraint_factors || [];
  // Convert new suitability factor format to old format if needed
  const suitability = convertToOldSuitabilityFormat(mapTask.suitability_factors || []);
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
