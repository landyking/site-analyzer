import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import { normalizeConstraints, type ConstraintDisplayItem } from './constraint-utils';

function ConstraintFactorsList({
  items,
  emptyMessage = 'No constraint factors selected',
  dense = true,
}: {
  items: Array<ConstraintDisplayItem | Record<string, unknown>>;
  emptyMessage?: string;
  dense?: boolean;
}) {
  const constraints = normalizeConstraints(items);
  if (!constraints.length) {
    return <Typography color="text.secondary">{emptyMessage}</Typography>;
  }
  return (
    <List dense={dense}>
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
                  mr: 1,
                }}
              >
                Distance from {label}
              </Typography>
              <Typography
                component="span"
                sx={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: 'success.main',
                }}
              >
                ≥ {Number.isFinite(cf.value) ? `${cf.value} m` : 'x m'}
              </Typography>
            </Box>
          </ListItem>
        );
      })}
    </List>
  );
}

export default ConstraintFactorsList;
