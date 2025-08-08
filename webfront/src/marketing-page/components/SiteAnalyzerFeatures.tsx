import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';

import SolarPowerIcon from '@mui/icons-material/SolarPower';
import TerrainIcon from '@mui/icons-material/Terrain';
import LayersIcon from '@mui/icons-material/Layers';
import AssessmentIcon from '@mui/icons-material/Assessment';
import MapIcon from '@mui/icons-material/Map';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const items = [
  {
    icon: <TerrainIcon sx={{ fontSize: 40 }} />,
    title: 'Geospatial Analysis',
    description:
      'Advanced GIS-based analysis considering topography, slope, and terrain characteristics for optimal solar panel placement.',
  },
  {
    icon: <LayersIcon sx={{ fontSize: 40 }} />,
    title: 'Multi-Factor Assessment',
    description:
      'Comprehensive evaluation including solar radiation, temperature, proximity to power lines, and land use constraints.',
  },
  {
    icon: <AssessmentIcon sx={{ fontSize: 40 }} />,
    title: 'Suitability Scoring',
    description:
      'Automated scoring system that weighs multiple factors to provide clear site suitability rankings and recommendations.',
  },
  {
    icon: <MapIcon sx={{ fontSize: 40 }} />,
    title: 'Interactive Visualization',
    description:
      'Rich map-based interface for exploring analysis results, viewing constraint layers, and comparing different sites.',
  },
  {
    icon: <CloudUploadIcon sx={{ fontSize: 40 }} />,
    title: 'Data Management',
    description:
      'Secure file upload and management system for analysis results, reports, and geospatial datasets.',
  },
  {
    icon: <SolarPowerIcon sx={{ fontSize: 40 }} />,
    title: 'Solar Optimization',
    description:
      'Specialized algorithms designed specifically for solar power installations, considering industry best practices.',
  },
];

const StyledCard = styled(Card)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  padding: 0,
  height: '100%',
  backgroundColor: (theme.vars || theme).palette.background.paper,
  '&:hover': {
    backgroundColor: 'transparent',
    cursor: 'pointer',
    boxShadow: (theme.vars || theme).shadows[4],
    transform: 'translateY(-2px)',
    transition: 'all 0.3s ease-in-out',
  },
  ...theme.applyStyles('dark', {
    backgroundColor: (theme.vars || theme).palette.grey[900],
    '&:hover': {
      backgroundColor: 'transparent',
      boxShadow: '0 8px 20px rgba(255, 193, 7, 0.2)',
    },
  }),
}));

const StyledCardContent = styled(CardContent)({
  display: 'flex',
  flexDirection: 'column',
  gap: 4,
  padding: 24,
  flexGrow: 1,
  '&:last-child': {
    paddingBottom: 24,
  },
});

const StyledTypography = styled(Typography)({
  display: '-webkit-box',
  WebkitBoxOrient: 'vertical',
  WebkitLineClamp: 2,
  overflow: 'hidden',
  textOverflow: 'ellipsis',
});

export default function SiteAnalyzerFeatures() {
  return (
    <Container id="features" sx={{ py: { xs: 8, sm: 16 } }}>
      <Box sx={{ mb: 6, textAlign: 'center' }}>
        <Typography
          component="h2"
          variant="h4"
          gutterBottom
          sx={{ color: 'text.primary', mb: 2 }}
        >
          Comprehensive Solar Site Analysis
        </Typography>
        <Typography
          variant="body1"
          sx={{ 
            color: 'text.secondary', 
            maxWidth: 800, 
            mx: 'auto',
            mb: 4 
          }}
        >
          Our platform combines cutting-edge GIS technology with solar industry expertise 
          to provide comprehensive site suitability analysis. From terrain evaluation to 
          regulatory compliance, we help you make informed decisions for solar installations.
        </Typography>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={2}
          sx={{ justifyContent: 'center' }}
        >
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<AssessmentIcon />}
          >
            Start New Analysis
          </Button>
          <Button
            variant="outlined"
            color="primary"
            size="large"
            startIcon={<MapIcon />}
          >
            View Sample Results
          </Button>
        </Stack>
      </Box>
      
      <Box 
        sx={{ 
          display: 'grid', 
          gridTemplateColumns: { 
            xs: '1fr', 
            sm: '1fr 1fr', 
            md: '1fr 1fr 1fr' 
          }, 
          gap: 3,
          mt: 6
        }}
      >
        {items.map((item, index) => (
          <StyledCard variant="outlined" key={index}>
            <StyledCardContent>
              <Box
                sx={{
                  color: 'primary.main',
                  mb: 1,
                }}
              >
                {item.icon}
              </Box>
              <div>
                <Typography
                  gutterBottom
                  sx={{ fontWeight: 'medium' }}
                  component="h3"
                  variant="h6"
                >
                  {item.title}
                </Typography>
                <StyledTypography
                  variant="body2"
                  sx={{ color: 'text.secondary' }}
                >
                  {item.description}
                </StyledTypography>
              </div>
            </StyledCardContent>
          </StyledCard>
        ))}
      </Box>
    </Container>
  );
}
