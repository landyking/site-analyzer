import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import PageContainer from './PageContainer';
import { VictoryChart, VictoryTheme, VictoryHistogram } from 'victory';

const sampleHistogramData = [
  { x: 1 },
  { x: 2 },
  { x: 2 },
  { x: 3 },
  { x: 3 },
  { x: 3 },
  { x: 4 },
  { x: 4 },
  { x: 5 }
];

export default function Tasks() {
  return (
    <PageContainer title="Tasks" breadcrumbs={[{ title: 'Tasks' }]}>
      <Box>
        <Typography color="text.secondary">
          Track and manage background processing tasks.
        </Typography>
        <VictoryChart
  domainPadding={20}
  theme={VictoryTheme.clean}
>
  <VictoryHistogram
    data={sampleHistogramData}
  />
</VictoryChart>
      </Box>
    </PageContainer>
  );
}
