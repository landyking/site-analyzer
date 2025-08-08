import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import { styled, alpha } from '@mui/material/styles';

import UploadFileIcon from '@mui/icons-material/UploadFile';
import SettingsIcon from '@mui/icons-material/Settings';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import MapIcon from '@mui/icons-material/Map';
import GetAppIcon from '@mui/icons-material/GetApp';

const items = [
  {
    icon: <UploadFileIcon fontSize="large" />,
    title: 'Prepare Data',
    description:
      'Built-in geospatial datasets ready for analysis.',
    upcomingFeature: 'Custom data upload support coming soon',
    hasUpcoming: true,
  },
  {
    icon: <SettingsIcon fontSize="large" />,
    title: 'Configure Analysis',
    description:
      'Set analysis parameters, weight factors, and specify constraints for your solar site assessment.',
  },
  {
    icon: <AnalyticsIcon fontSize="large" />,
    title: 'Run Analysis',
    description:
      'Our GIS engine processes your data considering multiple factors to generate suitability scores.',
  },
  {
    icon: <MapIcon fontSize="large" />,
    title: 'Explore Results',
    description:
      'Interactive maps and visualizations help you understand analysis results and site rankings.',
  },
  {
    icon: <GetAppIcon fontSize="large" />,
    title: 'Download Reports',
    description:
      'Export detailed analysis reports, suitability maps, and processed datasets for further use.',
  },
];

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  backgroundColor: alpha(theme.palette.primary.light, 0.05),
  border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
  transition: 'all 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-4px)',
    backgroundColor: alpha(theme.palette.primary.light, 0.1),
    border: `1px solid ${alpha(theme.palette.primary.main, 0.4)}`,
    boxShadow: `0 8px 25px ${alpha(theme.palette.primary.main, 0.15)}`,
  },
  ...theme.applyStyles('dark', {
    backgroundColor: alpha(theme.palette.primary.dark, 0.1),
    border: `1px solid ${alpha(theme.palette.primary.light, 0.2)}`,
    '&:hover': {
      backgroundColor: alpha(theme.palette.primary.dark, 0.2),
      border: `1px solid ${alpha(theme.palette.primary.light, 0.4)}`,
      boxShadow: `0 8px 25px ${alpha(theme.palette.primary.light, 0.15)}`,
    },
  }),
}));

const StyledCardContent = styled(CardContent)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  textAlign: 'center',
  gap: theme.spacing(2),
  padding: theme.spacing(3),
  '&:last-child': {
    paddingBottom: theme.spacing(3),
  },
}));

const StepNumber = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: -12,
  left: 20,
  width: 24,
  height: 24,
  borderRadius: '50%',
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '0.875rem',
  fontWeight: 'bold',
  boxShadow: theme.shadows[2],
}));

export default function SiteAnalyzerHighlights() {
  return (
    <Container id="highlights" sx={{ py: { xs: 8, sm: 16 } }}>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography
          component="h2"
          variant="h4"
          gutterBottom
          sx={{ 
            color: 'text.primary',
            fontWeight: 'bold',
            mb: 2,
          }}
        >
          How Site Analysis Works
        </Typography>
        <Typography
          variant="h6"
          sx={{ 
            color: 'text.secondary',
            maxWidth: '600px',
            mx: 'auto',
            fontWeight: 300,
          }}
        >
          A streamlined workflow from data input to actionable insights for solar site selection
        </Typography>
      </Box>
      
      <Box 
        sx={{ 
          display: 'grid', 
          gridTemplateColumns: { 
            xs: '1fr', 
            sm: 'repeat(2, 1fr)', 
            md: 'repeat(3, 1fr)',
            lg: 'repeat(5, 1fr)'
          }, 
          gap: 3,
          maxWidth: '1200px',
          mx: 'auto',
        }}
      >
        {items.map((item, index) => (
          <Box key={index} sx={{ position: 'relative' }}>
            <StepNumber>{index + 1}</StepNumber>
            <StyledCard>
              <StyledCardContent>
                <Box
                  sx={{
                    color: 'primary.main',
                    mb: 1,
                  }}
                >
                  {item.icon}
                </Box>
                <Typography
                  gutterBottom
                  sx={{ 
                    fontWeight: 'medium', 
                    fontSize: '1.1rem',
                    color: 'text.primary',
                  }}
                  component="h3"
                  variant="h6"
                >
                  {item.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ 
                    color: 'text.secondary',
                    lineHeight: 1.6,
                  }}
                >
                  {item.description}
                  {item.hasUpcoming && item.upcomingFeature && (
                    <Typography
                      component="span"
                      variant="body2"
                      sx={{
                        display: 'block',
                        mt: 1.5,
                        color: 'primary.main',
                        fontWeight: 'medium',
                        fontSize: '0.9rem',
                        fontStyle: 'italic',
                        position: 'relative',
                        '&::before': {
                          content: '"✨"',
                          mr: 0.5,
                        }
                      }}
                    >
                      {item.upcomingFeature}
                    </Typography>
                  )}
                </Typography>
              </StyledCardContent>
            </StyledCard>
          </Box>
        ))}
      </Box>
    </Container>
  );
}
