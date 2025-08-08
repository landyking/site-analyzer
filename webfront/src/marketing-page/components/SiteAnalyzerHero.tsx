import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import SolarPowerIcon from '@mui/icons-material/SolarPower';
import MapIcon from '@mui/icons-material/Map';
import AnalyticsIcon from '@mui/icons-material/Analytics';

const StyledBox = styled('div')(({ theme }) => ({
  alignSelf: 'center',
  width: '100%',
  height: 400,
  marginTop: theme.spacing(8),
  borderRadius: (theme.vars || theme).shape.borderRadius,
  outline: '6px solid',
  outlineColor: 'hsla(220, 25%, 80%, 0.2)',
  border: '1px solid',
  borderColor: (theme.vars || theme).palette.grey[200],
  boxShadow: '0 0 12px 8px hsla(220, 25%, 80%, 0.2)',
  backgroundImage: `linear-gradient(135deg, 
    rgba(255, 193, 7, 0.1) 0%, 
    rgba(76, 175, 80, 0.1) 50%, 
    rgba(33, 150, 243, 0.1) 100%),
    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500"><defs><pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M 50 0 L 0 0 0 50" fill="none" stroke="%23e0e0e0" stroke-width="1" opacity="0.3"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grid)"/></svg>')`,
  backgroundSize: 'cover',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  position: 'relative',
  overflow: 'hidden',
  [theme.breakpoints.up('sm')]: {
    marginTop: theme.spacing(10),
    height: 500,
  },
  ...theme.applyStyles('dark', {
    boxShadow: '0 0 24px 12px hsla(210, 100%, 25%, 0.2)',
    backgroundImage: `linear-gradient(135deg, 
      rgba(255, 193, 7, 0.2) 0%, 
      rgba(76, 175, 80, 0.2) 50%, 
      rgba(33, 150, 243, 0.2) 100%),
      url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500"><defs><pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M 50 0 L 0 0 0 50" fill="none" stroke="%23424242" stroke-width="1" opacity="0.3"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grid)"/></svg>')`,
    outlineColor: 'hsla(220, 20%, 42%, 0.1)',
    borderColor: (theme.vars || theme).palette.grey[700],
  }),
}));

const FeatureIcon = styled(Box)(({ theme }) => ({
  position: 'absolute',
  opacity: 0.1,
  color: theme.palette.primary.main,
  '&.solar': {
    top: '20%',
    left: '15%',
    fontSize: '4rem',
  },
  '&.map': {
    top: '60%',
    right: '20%',
    fontSize: '3rem',
  },
  '&.analytics': {
    bottom: '20%',
    left: '20%',
    fontSize: '3.5rem',
  },
}));

export default function SiteAnalyzerHero() {
  return (
    <Box
      id="hero"
      sx={(theme) => ({
        width: '100%',
        backgroundRepeat: 'no-repeat',
        backgroundImage:
          'radial-gradient(ellipse 80% 50% at 50% -20%, hsl(45, 100%, 90%), transparent)',
        ...theme.applyStyles('dark', {
          backgroundImage:
            'radial-gradient(ellipse 80% 50% at 50% -20%, hsl(45, 100%, 16%), transparent)',
        }),
      })}
    >
      <Container
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          pt: { xs: 14, sm: 20 },
          pb: { xs: 8, sm: 12 },
        }}
      >
        <Stack
          spacing={2}
          useFlexGap
          sx={{ alignItems: 'center', width: { xs: '100%', sm: '70%' } }}
        >
          <Typography
            variant="h1"
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              alignItems: 'center',
              fontSize: 'clamp(2.5rem, 8vw, 3.5rem)',
              textAlign: 'center',
            }}
          >
            Solar Power&nbsp;
            <Typography
              component="span"
              variant="h1"
              sx={(theme) => ({
                fontSize: 'inherit',
                color: 'primary.main',
                ...theme.applyStyles('dark', {
                  color: 'primary.light',
                }),
              })}
            >
              Site Analyzer
            </Typography>
          </Typography>
          <Typography
            variant="h5"
            sx={{
              textAlign: 'center',
              color: 'text.secondary',
              width: { sm: '100%', md: '80%' },
              fontWeight: 300,
              mb: 2,
            }}
          >
            Advanced Geospatial Analysis for Solar Installation Suitability
          </Typography>
          <Typography
            sx={{
              textAlign: 'center',
              color: 'text.secondary',
              width: { sm: '100%', md: '80%' },
              fontSize: '1.1rem',
            }}
          >
            Analyze geographical areas for optimal solar power site placement using comprehensive 
            constraint and suitability factors. Make informed decisions with our powerful 
            GIS-based analysis platform.
          </Typography>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            useFlexGap
            sx={{ pt: 3, width: { xs: '100%', sm: 'auto' } }}
          >
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<AnalyticsIcon />}
              sx={{ 
                minWidth: 'fit-content',
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
              }}
            >
              Start Analysis
            </Button>
            <Button
              variant="outlined"
              color="primary"
              size="large"
              startIcon={<MapIcon />}
              sx={{ 
                minWidth: 'fit-content',
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
              }}
            >
              View Demo
            </Button>
          </Stack>
        </Stack>
        <StyledBox id="image">
          <FeatureIcon className="solar">
            <SolarPowerIcon fontSize="inherit" />
          </FeatureIcon>
          <FeatureIcon className="map">
            <MapIcon fontSize="inherit" />
          </FeatureIcon>
          <FeatureIcon className="analytics">
            <AnalyticsIcon fontSize="inherit" />
          </FeatureIcon>
          <Typography
            variant="h6"
            sx={{
              color: 'primary.main',
              fontWeight: 'bold',
              textAlign: 'center',
              opacity: 0.8,
            }}
          >
            Interactive Analysis Dashboard
          </Typography>
        </StyledBox>
      </Container>
    </Box>
  );
}
