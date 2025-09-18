import { useState, useEffect, useMemo } from 'react';
import PageContainer from './PageContainer';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import type { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button'; // retained for table action buttons (View)
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
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
// Link removed (replaced by Button in actions)
import { alpha } from '@mui/material/styles';

import { AdminService, type AdminAdminGetMapTasksResponse, type MapTask } from '../../client';
import { useQuery } from '@tanstack/react-query';

// Inline hook (previously in hooks/useAdminMapTasks.ts) to simplify local usage
interface AdminMapTasksParams {
  page: number; pageSize: number; name?: string; status?: number;
}
function useAdminMapTasks({ page, pageSize, name, status }: AdminMapTasksParams) {
  return useQuery<AdminAdminGetMapTasksResponse>({
    queryKey: ['admin', 'map-tasks', { page, pageSize, name, status }],
    queryFn: () => AdminService.adminGetMapTasks({ currentPage: page, pageSize, name, status }),
  });
}

function formatDate(value?: string | null) {
  if (!value) return '-';
  try {
    const d = new Date(value);
    return new Intl.DateTimeFormat(undefined, { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).format(d);
  } catch { return value; }
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

function statusColor(desc?: string | null): 'default' | 'success' | 'error' | 'warning' | 'info' {
  const label = (desc || '').toLowerCase();
  if (label.includes('success') || label.includes('complete')) return 'success';
  if (label.includes('fail') || label.includes('error')) return 'error';
  if (label.includes('cancel')) return 'warning';
  if (label.includes('process') || label.includes('running')) return 'info';
  return 'default';
}

export default function Tasks() {
  const [nameInput, setNameInput] = useState('');
  const [name, setName] = useState(''); // debounced value
  // status mapping: 1 Pending, 2 Processing, 3 Success, 4 Failure, 5 Cancelled
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'processing' | 'success' | 'failure' | 'cancelled'>('all');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  // Debounce name filter
  useEffect(() => {
    const t = setTimeout(() => setName(nameInput), 300);
    return () => clearTimeout(t);
  }, [nameInput]);


  // Map status filter to backend numeric or leave undefined (TODO: confirm mapping)
  const statusParam = useMemo(() => {
    switch (statusFilter) {
      case 'pending': return 1;
      case 'processing': return 2;
      case 'success': return 3;
      case 'failure': return 4;
      case 'cancelled': return 5;
      default: return undefined;
    }
  }, [statusFilter]);

  const { data, isLoading, isError, error, refetch } = useAdminMapTasks({ page, pageSize, name: name || undefined, status: statusParam });
  const list: MapTask[] = (data?.list ?? []) as MapTask[];
  const total = (data?.total ?? list.length) || 0;
  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  useEffect(() => { if (page > pageCount) setPage(pageCount); }, [page, pageCount]);
  const rangeStart = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const rangeEnd = total === 0 ? 0 : Math.min(page * pageSize, total);

  const handlePageSizeChange = (e: SelectChangeEvent) => { const v = Number(e.target.value); setPageSize(v); setPage(1); };

  const PageSizeSelect = (
    <Stack direction="row" spacing={0.75} alignItems="center">
      <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>Rows per page:</Typography>
      <Select size="small" value={String(pageSize)} onChange={handlePageSizeChange} sx={{ height: 32, '& .MuiSelect-select': { py: 0.5 }, minWidth: 70 }}>
        {[5,10,20].map(n => <MenuItem key={n} value={String(n)}>{n}</MenuItem>)}
      </Select>
    </Stack>
  );

  const navBtnSx = { width: 26, height: 26, p: 0, '& .MuiSvgIcon-root': { fontSize: 18 } } as const;

  return (
    <PageContainer title="Tasks" breadcrumbs={[{ title: 'Tasks' }]}>      
      <Stack spacing={2}>
        <Typography color="text.secondary">Track and manage background processing tasks.</Typography>
        <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, background: (t) => alpha(t.palette.background.paper, 0.7) }}>
          {/* Filters Row */}
          <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center" sx={{ mb: 1 }}>
            <TextField size="small" placeholder="Name" value={nameInput} onChange={(e) => { setNameInput(e.target.value); setPage(1); }} sx={{ width: 140 }} />
            <Select size="small" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value as typeof statusFilter); setPage(1); }} sx={{ width: 150 }} displayEmpty>
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="processing">Processing</MenuItem>
              <MenuItem value="success">Success</MenuItem>
              <MenuItem value="failure">Failure</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
            </Select>
            {/* Search button removed: queries fire automatically via debounce & filter state changes */}
          </Stack>
          <Divider sx={{ mb: 1 }} />
          {/* Table */}
          <Box sx={{ width: '100%', overflowX: 'auto' }}>
            <Table size="small" sx={{ '& th, & td': { whiteSpace: 'nowrap' } }}>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>District</TableCell>
                  <TableCell>Created At</TableCell>
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
                    <TableCell>{formatDate(task.created_at)}</TableCell>
                    <TableCell>{formatDate(task.started_at)}</TableCell>
                    <TableCell>{formatDate(task.ended_at)}</TableCell>
                    <TableCell>{formatElapsed(task.started_at, task.ended_at)}</TableCell>
                    <TableCell>
                      <Chip size="small" label={task.status_desc ?? task.status} color={statusColor(task.status_desc)} variant={statusColor(task.status_desc)==='default' ? 'outlined' : 'filled'} />
                    </TableCell>
                    <TableCell>{task.user_email}</TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <Button size="small" startIcon={<VisibilityRoundedIcon />}>View</Button>
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
          {/* Pagination footer aligned with Users page */}
          <Stack direction="row" justifyContent="flex-end" alignItems="center" spacing={2} sx={{ mt: 1 }}>
            {PageSizeSelect}
            <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
              {rangeStart}-{rangeEnd} of {total}
            </Typography>
            <Stack direction="row" spacing={0.5} alignItems="center">
              <Tooltip title="Previous page">
                <span>
                  <IconButton size="small" sx={navBtnSx} disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>
                    <ChevronLeftIcon />
                  </IconButton>
                </span>
              </Tooltip>
              <Tooltip title="Next page">
                <span>
                  <IconButton size="small" sx={navBtnSx} disabled={page >= pageCount || rangeEnd >= total} onClick={() => setPage(p => Math.min(pageCount, p + 1))}>
                    <ChevronRightIcon />
                  </IconButton>
                </span>
              </Tooltip>
            </Stack>
          </Stack>
        </Paper>
      </Stack>
    </PageContainer>
  );
}
