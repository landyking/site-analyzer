import { useState, useEffect, useCallback } from 'react';
import PageContainer from './PageContainer';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
// Removed full Pagination in favor of custom compact footer controls
import Stack from '@mui/material/Stack';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import { alpha } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import LockIcon from '@mui/icons-material/Lock';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AdminService, type AdminAdminGetUserListResponse, type User4Admin } from '../../client';
import useNotifications from '../hooks/useNotifications/useNotifications';
import { useDialogs } from '../hooks/useDialogs/useDialogs';
import Select from '@mui/material/Select';
import type { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

// Date formatting helper
function formatDate(value?: string | null) {
  if (!value) return '-';
  try {
    const d = new Date(value);
    return new Intl.DateTimeFormat(undefined, {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
    }).format(d);
  } catch { return value; }
}

// Query hook isolated for reuse/testing
function useAdminUsers(params: { page: number; pageSize: number; keyword: string; status?: number | undefined }) {
  const { page, pageSize, keyword, status } = params;
  const query = useQuery<AdminAdminGetUserListResponse>({
    queryKey: ['admin', 'users', { page, pageSize, keyword, status }],
    queryFn: () => AdminService.adminGetUserList({ currentPage: page, pageSize, keyword: keyword || undefined, status }),
  });
  const data = query.data;
  const items: User4Admin[] = (data?.list || []).filter(u => u.id != null) as User4Admin[];
  return { ...query, items, total: data?.total ?? items.length, serverPageSize: data?.page_size, serverCurrentPage: data?.current_page };
}

// ---- Small Presentational Components ----
const SearchBox = ({ value, onChange }: { value: string; onChange: (v: string) => void }) => (
  <TextField
    size="small"
    placeholder="Search"
    value={value}
    onChange={(e) => onChange(e.target.value)}
    InputProps={{
      startAdornment: (
        <InputAdornment position="start">
          <SearchIcon fontSize="small" />
        </InputAdornment>
      ),
    }}
    sx={{ width: 260 }}
  />
);

const StatusChip = ({ locked }: { locked: boolean }) => (
  <Chip
    size="small"
    label={locked ? 'Locked' : 'Active'}
    color={locked ? 'warning' : 'success'}
    variant={locked ? 'outlined' : 'filled'}
  />
);

const LockToggleButton = ({ locked, onToggle, disabled }: { locked: boolean; onToggle: () => void; disabled?: boolean }) => (
  <Tooltip title={disabled ? 'Admin accounts cannot be locked' : (locked ? 'Unlock user' : 'Lock user')}>
    <span>
      <IconButton size="small" onClick={onToggle} color={locked ? 'warning' : 'default'} disabled={disabled}>
        {locked ? <LockOpenIcon fontSize="small" /> : <LockIcon fontSize="small" />}
      </IconButton>
    </span>
  </Tooltip>
);

interface UsersTableProps {
  users: User4Admin[];
  onToggleLock?: (id: number) => void; // optional until wired
  loading?: boolean;
}

const UsersTable = ({ users, onToggleLock, loading }: UsersTableProps) => (
  <Table size="small" aria-label="users table">
    <TableHead>
      <TableRow>
        <TableCell>Email</TableCell>
        <TableCell>Created At</TableCell>
        <TableCell>Last Login</TableCell>
        <TableCell>Status</TableCell>
        <TableCell align="right">Actions</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {loading ? (
        <TableRow><TableCell colSpan={5} align="center"><CircularProgress size={22} /></TableCell></TableRow>
      ) : users.length === 0 ? (
        <TableRow><TableCell colSpan={5} align="center">No users found</TableCell></TableRow>
      ) : users.map((u) => (
        <TableRow key={u.id} hover sx={{ '&:last-child td': { border: 0 } }}>
          <TableCell>{u.email || '(no email)'}</TableCell>
          <TableCell>{formatDate(u.created_at)}</TableCell>
          <TableCell>{formatDate(u.last_login)}</TableCell>
          <TableCell><StatusChip locked={u.status === 2} /></TableCell>
          <TableCell align="right">
            {onToggleLock && u.id != null ? (
              <LockToggleButton
                locked={u.status === 2}
                disabled={u.role === 1}
                onToggle={() => onToggleLock(u.id as number)}
              />
            ) : null}
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);

// ---- Main Page Component ----
export default function Users() {
  const queryClient = useQueryClient();
  const { show } = useNotifications();
  const { confirm } = useDialogs();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'locked'>('all');

  // Debounce search simple impl (no timer libs to keep concise)
  const [keyword, setKeyword] = useState('');
  useEffect(() => {
    const t = setTimeout(() => setKeyword(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const statusParam = statusFilter === 'all' ? undefined : (statusFilter === 'active' ? 1 : 2);
  const { items, isLoading, isError, error, total } = useAdminUsers({ page, pageSize, keyword, status: statusParam });
  const pageCount = Math.max(1, Math.ceil((total || 0) / pageSize));
  const rangeStart = total ? (total === 0 ? 0 : (page - 1) * pageSize + 1) : (items.length ? (page - 1) * pageSize + 1 : 0);
  const inferredTotal = total ?? (pageCount * pageSize); // fallback if server not yet responded
  const rangeEnd = total ? (total === 0 ? 0 : Math.min(page * pageSize, total)) : (rangeStart ? rangeStart + items.length - 1 : 0);

  // Reset page if out of bounds (e.g., keyword reduces total)
  useEffect(() => { if (page > pageCount) setPage(pageCount); }, [page, pageCount]);

  type CachedUserList = { list?: Array<{ id?: number | null; status?: number | null }> | null };
  const mutation = useMutation({
    mutationFn: (payload: { user_id: number; status: number }) =>
      AdminService.adminUpdateUserStatus({ requestBody: payload }),
    onMutate: async ({ user_id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['admin', 'users'] });
      const snapshots = queryClient.getQueriesData<CachedUserList>({ queryKey: ['admin', 'users'] });
      snapshots.forEach(([key, value]) => {
        if (value?.list) {
          const next = value.list.map(u => u?.id === user_id ? { ...u, status } : u);
          queryClient.setQueryData(key, { ...value, list: next });
        }
      });
      return { snapshots };
    },
    onError: (_err, _vars, ctx) => {
      ctx?.snapshots.forEach(([key, value]) => queryClient.setQueryData(key, value));
      show('Failed to update user status', { severity: 'error', autoHideDuration: 2500 });
    },
    onSuccess: (_data, vars) => {
      show(vars.status === 2 ? 'User locked' : 'User unlocked', { severity: 'success', autoHideDuration: 1800 });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
    },
  });

  const handleToggleLock = useCallback(async (user: User4Admin) => {
    if (user.id == null) return;
    const isLocked = user.status === 2;
    const nextStatus = isLocked ? 1 : 2; // 1 active, 2 locked
    const actionWord = isLocked ? 'Unlock' : 'Lock';
    const confirmed = await confirm(
      `Are you sure you want to ${actionWord.toLowerCase()} “${user.email}”?`,
      {
        title: `${actionWord} User`,
        okText: actionWord,
        cancelText: 'Cancel',
        severity: isLocked ? 'info' : 'warning',
      },
    );
    if (!confirmed) return;
    mutation.mutate({ user_id: user.id, status: nextStatus });
  }, [mutation, confirm]);

  const handlePageSizeChange = (e: SelectChangeEvent) => {
    const value = Number(e.target.value as string);
    setPageSize(value);
    setPage(1);
  };

  // Inline, compact page size selector aligned with Pagination height (~32px)
  const PageSizeSelect = (
    <Stack direction="row" spacing={0.75} alignItems="center">
        <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>Rows per page:</Typography>
      <Select
        size="small"
        value={String(pageSize)}
        onChange={handlePageSizeChange}
        sx={{
          height: 32,
          '& .MuiSelect-select': { py: 0.5, display: 'flex', alignItems: 'center' },
          minWidth: 70,
        }}
      >
        {[5, 10, 20].map((n) => (
          <MenuItem key={n} value={String(n)}>{n}</MenuItem>
        ))}
      </Select>
    </Stack>
  );

  const navBtnSx = { width: 26, height: 26, p: 0, '& .MuiSvgIcon-root': { fontSize: 18 } } as const;

  const StatusSelect = (
    <Stack direction="row" spacing={0.75} alignItems="center">
      <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>Status:</Typography>
      <Select
        size="small"
        value={statusFilter}
        onChange={(e: SelectChangeEvent) => { setStatusFilter(e.target.value as 'all' | 'active' | 'locked'); setPage(1); }}
        sx={{ height: 32, '& .MuiSelect-select': { py: 0.5 }, minWidth: 90 }}
      >
        <MenuItem value="all">All</MenuItem>
        <MenuItem value="active">Active</MenuItem>
        <MenuItem value="locked">Locked</MenuItem>
      </Select>
    </Stack>
  );

  return (
    <PageContainer title="Users" breadcrumbs={[{ title: 'Users' }]}>      
      <Stack spacing={2}>        
        <Typography color="text.secondary">
          Manage users, account status, and access.
        </Typography>
        <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, background: (t) => alpha(t.palette.background.paper, 0.7) }}>
          <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ xs: 'stretch', md: 'center' }} spacing={2} sx={{ mb: 1 }}>
            <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
              <SearchBox value={search} onChange={(v) => { setSearch(v); setPage(1); }} />
              {StatusSelect}
            </Stack>
          </Stack>
          <Divider sx={{ mb: 1 }} />
          <Box sx={{ width: '100%', overflowX: 'auto' }}>
            {isError ? (
              <Alert severity="error" action={<Button size="small" startIcon={<RefreshIcon />} onClick={() => setPage(page)}>Retry</Button>}>
                {error instanceof Error ? error.message : 'Failed to load users'}
              </Alert>
            ) : (
              <UsersTable users={items} onToggleLock={(id) => {
                const u = items.find(i => i.id === id);
                if (u) handleToggleLock(u);
              }} loading={isLoading || mutation.isPending} />
            )}
          </Box>
          <Stack direction="row" justifyContent="flex-end" alignItems="center" spacing={2} sx={{ mt: 1 }}>
            {PageSizeSelect}
            <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
              {rangeStart}-{rangeEnd} of {inferredTotal}
            </Typography>
            <Stack direction="row" spacing={0.5} alignItems="center">
              <Tooltip title="Previous page">
                <span>
                  <IconButton size="small" sx={navBtnSx} disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
                    <ChevronLeftIcon />
                  </IconButton>
                </span>
              </Tooltip>
              <Tooltip title="Next page">
                <span>
                  <IconButton size="small" sx={navBtnSx} disabled={page >= pageCount || rangeEnd >= inferredTotal} onClick={() => setPage((p) => Math.min(pageCount, p + 1))}>
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
