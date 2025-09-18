import { useState, useEffect, useMemo } from 'react';
import PageContainer from './PageContainer';
import { useNavigate } from '@tanstack/react-router';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import VisibilityRoundedIcon from '@mui/icons-material/VisibilityRounded';
import RefreshIcon from '@mui/icons-material/Refresh';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import TableBody from '@mui/material/TableBody';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import Divider from '@mui/material/Divider';
import { alpha } from '@mui/material/styles';

import { AdminService, type AdminAdminGetMapTasksResponse, type MapTask } from '../../client';
import { useQuery } from '@tanstack/react-query';
import { formatDate, formatElapsed } from './shared/tableFormatters';
import { CompactPagination } from './shared/TableUtils';
import { mapTaskStatusOptions, mapStatusFilterValueToCode, mapTaskStatusColor } from './shared/statusUtils';

interface AdminMapTasksParams {
  page: number; pageSize: number; name?: string; status?: number;
}
function useAdminMapTasks({ page, pageSize, name, status }: AdminMapTasksParams) {
  return useQuery<AdminAdminGetMapTasksResponse>({
    queryKey: ['admin', 'map-tasks', { page, pageSize, name, status }],
    queryFn: () => AdminService.adminGetMapTasks({ currentPage: page, pageSize, name, status }),
  });
}


// status color & mapping centralized in statusUtils

export default function Tasks() {
  const [nameInput, setNameInput] = useState('');
  const [name, setName] = useState(''); // debounced value
  const [statusFilter, setStatusFilter] = useState<'all' | string>('all');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const navigate = useNavigate();

  // Debounce name filter
  useEffect(() => {
    const t = setTimeout(() => setName(nameInput), 300);
    return () => clearTimeout(t);
  }, [nameInput]);


  const statusParam = useMemo(() => mapStatusFilterValueToCode(statusFilter), [statusFilter]);

  const { data, isLoading, isError, error, refetch } = useAdminMapTasks({ page, pageSize, name: name || undefined, status: statusParam });
  const list: MapTask[] = (data?.list ?? []) as MapTask[];
  const total = (data?.total ?? list.length) || 0;
  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  useEffect(() => { if (page > pageCount) setPage(pageCount); }, [page, pageCount]);
  const rangeStart = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const rangeEnd = total === 0 ? 0 : Math.min(page * pageSize, total);

  const openDetails = (task: MapTask) => {
    navigate({ to: `/dashboard/tasks/$taskId`, params: { taskId: String(task.id) } });
  };

  return (
    <PageContainer title="Tasks" breadcrumbs={[{ title: 'Tasks' }]}>      
      <Stack spacing={2}>
        <Typography color="text.secondary">Track and manage background processing tasks.</Typography>
        <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, background: (t) => alpha(t.palette.background.paper, 0.7) }}>
          {/* Filters Row */}
          <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center" sx={{ mb: 1 }}>
            <TextField size="small" placeholder="Name" value={nameInput} onChange={(e) => { setNameInput(e.target.value); setPage(1); }} sx={{ width: 140 }} />
            <Select
              size="small"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              sx={{ width: 150 }}
              displayEmpty
            >
              <MenuItem value="all">All</MenuItem>
              {mapTaskStatusOptions.map(opt => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </Select>
          </Stack>
          <Divider sx={{ mb: 1 }} />
          {/* Table */}
          <Box sx={{ width: '100%', overflowX: 'auto' }}>
            <Table size="small" sx={{ '& th, & td': { whiteSpace: 'nowrap' } }}>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>District</TableCell>
                  {/* <TableCell>Created At</TableCell> */}
                  <TableCell>Started At</TableCell>
                  <TableCell>Ended At</TableCell>
                  <TableCell>Elapse</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  <TableRow><TableCell colSpan={9} align="center"><Typography variant="body2" color="text.secondary">Loading…</Typography></TableCell></TableRow>
                ) : isError ? (
                  <TableRow><TableCell colSpan={9} align="center"><Typography color="error">Failed to load tasks</Typography></TableCell></TableRow>
                ) : list.length === 0 ? (
                  <TableRow><TableCell colSpan={9} align="center">No tasks</TableCell></TableRow>
                ) : list.map(task => (
                  <TableRow key={task.id} hover>
                    <TableCell>{task.name}</TableCell>
                    <TableCell>{task.district_name ?? task.district_code}</TableCell>
                    {/* <TableCell>{formatDate(task.created_at)}</TableCell> */}
                    <TableCell>{formatDate(task.started_at)}</TableCell>
                    <TableCell>{formatDate(task.ended_at)}</TableCell>
                    <TableCell>{formatElapsed(task.started_at, task.ended_at)}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={task.status_desc ?? task.status}
                        color={mapTaskStatusColor(task.status_desc)}
                        variant={mapTaskStatusColor(task.status_desc) === 'default' ? 'outlined' : 'filled'}
                      />
                    </TableCell>
                    <TableCell>{task.user_email}</TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <Button size="small" startIcon={<VisibilityRoundedIcon />} onClick={() => openDetails(task)}>View</Button>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {isError && (
              <Alert severity="error" sx={{ mt: 1 }} action={<Button size="small" startIcon={<RefreshIcon />} onClick={() => refetch()}>Retry</Button>}>
                {error instanceof Error ? error.message : 'Error fetching tasks'}
              </Alert>
            )}
          </Box>
          <CompactPagination
            page={page}
            pageSize={pageSize}
            total={total}
            pageCount={pageCount}
            rangeStart={rangeStart}
            rangeEnd={rangeEnd}
            onPageChange={setPage}
            onPageSizeChange={(s) => { setPageSize(s); setPage(1); }}
          />
        </Paper>
      </Stack>
    </PageContainer>
  );
}
