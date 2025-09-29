import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import { normalizeSuitabilityFactors, SUITABILITY_LABELS, type SuitabilityDisplayFactor } from './suitability-utils';

type Props = {
  items: Array<SuitabilityDisplayFactor | Record<string, unknown>>;
  emptyMessage?: string;
  dense?: boolean;
  labelsMap?: Record<string, string>;
};

function SuitabilityFactorsList({ items, emptyMessage = 'No suitability factors selected', dense = true, labelsMap = SUITABILITY_LABELS }: Props) {
  const suitability = normalizeSuitabilityFactors(items as unknown[]);
  if (!suitability.length) {
    return <Typography color="text.secondary">{emptyMessage}</Typography>;
  }
  return (
    <List dense={dense}>
      {suitability.map((sf) => {
        const label = labelsMap[sf.kind] ?? sf.label ?? sf.kind;
        const header = `${label} - Weight: ${Number.isFinite(sf.weight as number) ? sf.weight : '0'}`;
        return (
          <ListItem key={sf.kind} alignItems="flex-start" sx={{ display: 'block', py: 0 }}>
            <Typography component="div" sx={{ fontWeight: 500, mb: 0.5, color: 'secondary.main' }}>
              • {header}
            </Typography>
            <List dense sx={{ pl: 3 }}>
              {sf.ranges.map((r, idx) => {
                let condition = '';
                const sFinite = Number.isFinite(r.start as number);
                const eFinite = Number.isFinite(r.end as number);
                if (sFinite && eFinite) {
                  condition = `${r.start} ≤ value < ${r.end}`;
                } else if (sFinite) {
                  condition = `value ≥ ${r.start}`;
                } else if (eFinite) {
                  condition = `value < ${r.end}`;
                }
                const pts = Number.isFinite(r.points as number) ? `${r.points} points` : 'x points';
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
                            mr: 1,
                          }}
                        >
                          {condition}
                        </Typography>
                        <Typography
                          component="span"
                          sx={{ fontSize: '0.875rem', fontWeight: 600, color: 'success.main' }}
                        >
                          {pts}
                        </Typography>
                      </Box>
                    ) : (
                      <Typography sx={{ color: 'success.main', fontWeight: 500 }}>{pts}</Typography>
                    )}
                  </ListItem>
                );
              })}
            </List>
          </ListItem>
        );
      })}
    </List>
  );
}

export default SuitabilityFactorsList;
