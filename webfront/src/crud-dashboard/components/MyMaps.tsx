import * as React from 'react';
import { useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Divider from '@mui/material/Divider';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import RefreshRoundedIcon from '@mui/icons-material/RefreshRounded';
import VisibilityRoundedIcon from '@mui/icons-material/VisibilityRounded';
import DownloadRoundedIcon from '@mui/icons-material/DownloadRounded';
import CancelRoundedIcon from '@mui/icons-material/CancelRounded';
import CircularProgress from '@mui/material/CircularProgress';

import PageContainer from './PageContainer';
import { OpenAPI, UserService, type MapTaskDetails } from '../../client';
import useNotifications from '../hooks/useNotifications/useNotifications';
import { useDialogs } from '../hooks/useDialogs/useDialogs';

function formatDate(value?: string | null) {
  if (!value) return '-';
  try {
    const d = new Date(value);
    return new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).format(d);
  } catch {
    return value;
  }
}

function formatElapsed(start?: string | null, end?: string | null) {
  const startMs = start ? Date.parse(start) : NaN;
  const endMs = end ? Date.parse(end) : Date.now();
  if (Number.isNaN(startMs) || Number.isNaN(endMs)) return '-';
  const ms = Math.max(0, endMs - startMs);
  const minutes = Math.floor(ms / 60000);
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (hours > 0) return `${hours}h ${remainingMinutes}m`;
  if (minutes > 0) return `${minutes}m`;
  const seconds = Math.floor(ms / 1000);
  return `${seconds}s`;
}

function statusColor(desc?: string | null): 'default' | 'success' | 'error' | 'warning' {
  const label = (desc || '').toLowerCase();
  if (label.includes('success')) return 'success';
  if (label.includes('fail') || label.includes('error')) return 'error';
  if (label.includes('cancel')) return 'warning';
  return 'default';
}

function getFirstFileUrl(task: MapTaskDetails): string | null {
  const f = task.files && task.files.length > 0 ? task.files[0] : null;
  if (!f) return null;
  const p = f.file_path || '';
  if (/^https?:\/\//i.test(p)) return p;
  // If server returns a relative path, prefix with API BASE
  return `${OpenAPI.BASE ?? ''}${p.startsWith('/') ? p : `/${p}`}`;
}

function Section({ title, actions, children }: { title: string; actions?: React.ReactNode; children: React.ReactNode }) {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <Typography variant="h6" sx={{ fontWeight: 700 }}>{title}</Typography>
        <Box sx={{ flex: 1 }} />
        {actions}
      </Stack>
      <Divider sx={{ mb: 2 }} />
      {children}
    </Paper>
  );
}

export default function MyMaps() {
  const queryClient = useQueryClient();
  const { show } = useNotifications();
  const { confirm } = useDialogs();

  const { data: ongoing, isLoading: loadingOngoing, refetch: refetchOngoing } = useQuery({
    queryKey: ['my-map-tasks', { completed: false }],
    queryFn: () => UserService.userGetMyMapTasks({ completed: false }),
  });

  const { data: completed, isLoading: loadingCompleted, refetch: refetchCompleted } = useQuery({
    queryKey: ['my-map-tasks', { completed: true }],
    queryFn: () => UserService.userGetMyMapTasks({ completed: true }),
  });

  const cancelMutation = useMutation({
    mutationFn: (taskId: number) => UserService.userCancelMapTask({ taskId }),
    onSuccess: () => {
      show('Task cancelled', { severity: 'success', autoHideDuration: 2000 });
      // refresh both lists
      queryClient.invalidateQueries({ queryKey: ['my-map-tasks'] });
    },
  });

  const ongoingRows = useMemo(() => ongoing?.list ?? [], [ongoing]);
  const completedRows = useMemo(() => completed?.list ?? [], [completed]);

  const actions = (
    <IconButton aria-label="refresh" onClick={() => { refetchOngoing(); refetchCompleted(); }}>
      <RefreshRoundedIcon />
    </IconButton>
  );

  const openDetails = () => {
    // Details not implemented yet
  };

  const handleCancel = (task: MapTaskDetails) => {
    void confirm(
      <>Are you sure you want to cancel “{task.name}”?<br/>This will stop processing and cannot be undone.</>,
      {
        title: 'Cancel task?',
        okText: 'Yes, cancel',
        cancelText: 'Keep running',
        severity: 'warning',
      },
    ).then((ok) => {
      if (ok) {
        cancelMutation.mutate(task.id);
      }
    });
  };

  return (
    <PageContainer title="My Maps" breadcrumbs={[{ title: 'My Maps' }]} actions={actions}>
      <Stack spacing={3}>
        <Section title="Ongoing">
          <TableContainer>
            <Table size="small" aria-label="ongoing map tasks">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>District</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Created At</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Elapse</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 700 }} align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loadingOngoing ? (
                  <TableRow>
                    <TableCell colSpan={6}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <CircularProgress size={18} />
                        <Typography color="text.secondary">Loading…</Typography>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ) : ongoingRows.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6}>
                      <Typography color="text.secondary">No ongoing tasks.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  ongoingRows.map((row) => (
                    <TableRow key={row.id} hover>
                      <TableCell>{row.name}</TableCell>
                      <TableCell>{row.district_name ?? row.district_code}</TableCell>
                      <TableCell>{formatDate(row.created_at)}</TableCell>
                      <TableCell>{formatElapsed(row.started_at ?? row.created_at, undefined)}</TableCell>
                      <TableCell>
                        <Chip size="small" color={statusColor(row.status_desc)} label={row.status_desc ?? row.status} />
                      </TableCell>
                      <TableCell align="right">
                        <Stack direction="row" spacing={1} justifyContent="flex-end">
                          <Button size="small" startIcon={<CancelRoundedIcon />} disabled={cancelMutation.isPending} onClick={() => handleCancel(row)}>
                            Cancel
                          </Button>
                          <Button size="small" startIcon={<VisibilityRoundedIcon />} onClick={openDetails}>View</Button>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Section>

        <Section title="Completed">
          <TableContainer>
            <Table size="small" aria-label="completed map tasks">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>District</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Ended At</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Created At</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Elapse</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 700 }} align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loadingCompleted ? (
                  <TableRow>
                    <TableCell colSpan={7}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <CircularProgress size={18} />
                        <Typography color="text.secondary">Loading…</Typography>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ) : completedRows.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7}>
                      <Typography color="text.secondary">No completed tasks yet.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  completedRows.map((row) => {
                    const downloadUrl = getFirstFileUrl(row);
                    return (
                      <TableRow key={row.id} hover>
                        <TableCell>{row.name}</TableCell>
                        <TableCell>{row.district_name ?? row.district_code}</TableCell>
                        <TableCell>{formatDate(row.ended_at)}</TableCell>
                        <TableCell>{formatDate(row.created_at)}</TableCell>
                        <TableCell>{formatElapsed(row.started_at ?? row.created_at, row.ended_at)}</TableCell>
                        <TableCell>
                          <Chip size="small" color={statusColor(row.status_desc)} label={row.status_desc ?? row.status} />
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            {downloadUrl ? (
                              <Button size="small" startIcon={<DownloadRoundedIcon />} component="a" href={downloadUrl} target="_blank" rel="noreferrer">
                                Download
                              </Button>
                            ) : (
                              <Button size="small" startIcon={<DownloadRoundedIcon />} disabled>
                                Download
                              </Button>
                            )}
                            <Button size="small" startIcon={<VisibilityRoundedIcon />} onClick={openDetails}>View</Button>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Section>
      </Stack>

    </PageContainer>
  );
}
