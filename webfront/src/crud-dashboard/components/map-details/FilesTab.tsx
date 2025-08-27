import { Box, List, ListItem, ListItemIcon, ListItemText, Link, Typography } from '@mui/material';
import InsertDriveFileRoundedIcon from '@mui/icons-material/InsertDriveFileRounded';
import DownloadRoundedIcon from '@mui/icons-material/DownloadRounded';
import type { UserUserGetMapTaskResponse } from '../../../client/types.gen';

export default function FilesTab({ mapTask }: { mapTask: NonNullable<UserUserGetMapTaskResponse['data']> }) {
  const files = Array.isArray(mapTask.files) ? mapTask.files : [];
  if (!files.length) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">No files available for this map.</Typography>
      </Box>
    );
  }
  return (
    <Box sx={{ p: 2 }}>
      <List>
        {files.map((file, idx) => (
          <ListItem key={file.file_path || idx} sx={{ borderBottom: '1px solid #eee' }}
            secondaryAction={
              <Link href={file.file_path} target="_blank" rel="noopener" download underline="none">
                <DownloadRoundedIcon color="primary" />
              </Link>
            }
          >
            <ListItemIcon>
              <InsertDriveFileRoundedIcon color="action" />
            </ListItemIcon>
            <ListItemText
              primary={file.file_type}
              secondary={undefined}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}
