
import { useQuery } from '@tanstack/react-query';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import LinearProgress from '@mui/material/LinearProgress';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Tooltip from '@mui/material/Tooltip';
import type { MapTaskDetails, MapTaskProgress } from '../../client/types.gen';
import { UserService } from '../../client/sdk.gen';

interface ProgressTabProps {
	mapTask?: MapTaskDetails | null;
}

function formatTime(dt?: string) {
	if (!dt) return '-';
	const d = new Date(dt);
	if (isNaN(d.getTime())) return dt;
	return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}




const ProgressTab: React.FC<ProgressTabProps> = ({ mapTask }) => {
	const taskId = mapTask?.id;
	// If status < 3, task is ongoing, so poll every 3s. Otherwise, fetch once.
	const shouldPoll = typeof mapTask?.status === 'number' && mapTask.status < 3;
	const { data, isLoading, isError, error } = useQuery({
		queryKey: ['userGetMapTaskProgress', taskId],
		queryFn: () => UserService.userGetMapTaskProgress({ taskId: Number(taskId) }),
		enabled: !!taskId,
		refetchInterval: shouldPoll ? 3000 : undefined,
	});

	const progressList: MapTaskProgress[] = (data?.list || []).slice().reverse(); // latest on top
	const percent = progressList.length > 0 ? Math.max(...progressList.map((item) => item.percent)) : 0;

	return (
		<Paper  sx={{ p: 2, mb: 1 }}>
			{isLoading ? (
				<Typography color="text.secondary">Loading progress...</Typography>
			) : isError ? (
				<Alert severity="error">{error instanceof Error ? error.message : 'Failed to load progress.'}</Alert>
			) : (
				<>
					<Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
						<Box sx={{ flex: 1 }}>
							<LinearProgress variant="determinate" value={percent} sx={{ height: 8, borderRadius: 4 }} />
						</Box>
						<Typography sx={{ minWidth: 48, fontWeight: 500 }}>{percent}%</Typography>
					</Box>
					<List dense disablePadding>
						{progressList.map((item, idx) => (
							<>
								<ListItem key={item.id} sx={{ px: 0, py: 0.5, display: 'flex', alignItems: 'center' }}>
									<Tooltip title={item.created_at ? new Date(item.created_at).toLocaleString() : ''} arrow>
										<Typography sx={{ minWidth: 72, color: 'text.secondary', fontSize: 14, cursor: 'pointer' }}>
											{formatTime(item.created_at)}
										</Typography>
									</Tooltip>
									{item.phase && (
										<Chip
											label={item.phase}
											size="small"
											color="primary"
											sx={{ mx: 1, fontWeight: 600, textTransform: 'lowercase', fontSize: 13 }}
										/>
									)}
									<Typography sx={{ fontSize: 15, color: item.error_msg ? 'error.main' : 'text.primary', fontWeight: item.error_msg ? 600 : 400 }}>
										{item.error_msg ? item.error_msg : item.description}
									</Typography>
									{/* Show spinner after the top (latest) item if ongoing */}
									{shouldPoll && idx === 0 && (
										<CircularProgress size={18} sx={{ ml: 2 }} />
									)}
								</ListItem>
							</>
						))}
					</List>
				</>
			)}
		</Paper>
	);
};

export default ProgressTab;
