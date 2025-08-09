import * as React from 'react';
import { styled, alpha } from '@mui/material/styles';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import MenuItem from '@mui/material/MenuItem';
import Drawer from '@mui/material/Drawer';
import MenuIcon from '@mui/icons-material/Menu';
import CloseRoundedIcon from '@mui/icons-material/CloseRounded';
import SolarPowerIcon from '@mui/icons-material/SolarPower';
import ColorModeIconDropdown from '../../shared-theme/ColorModeIconDropdown';
import Typography from '@mui/material/Typography';
import { Link as RouterLink, useNavigate } from '@tanstack/react-router';

const StyledToolbar = styled(Toolbar)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  flexShrink: 0,
  borderRadius: `calc(${theme.shape.borderRadius}px + 8px)`,
  backdropFilter: 'blur(24px)',
  border: '1px solid',
  borderColor: (theme.vars || theme).palette.divider,
  backgroundColor: theme.vars
    ? `rgba(${theme.vars.palette.background.defaultChannel} / 0.4)`
    : alpha(theme.palette.background.default, 0.4),
  boxShadow: (theme.vars || theme).shadows[1],
  padding: '8px 12px',
}));

export default function SiteAnalyzerAppBar() {
  const [open, setOpen] = React.useState(false);
  const navigate = useNavigate();

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpen(newOpen);
  };

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
    // Close mobile menu if open
    setOpen(false);
  };

  return (
    <AppBar
      position="fixed"
      enableColorOnDark
      sx={{
        boxShadow: 0,
        bgcolor: 'transparent',
        backgroundImage: 'none',
        mt: 'calc(var(--template-frame-height, 0px) + 28px)',
      }}
    >
      <Container maxWidth="lg">
        <StyledToolbar variant="dense" disableGutters>
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', px: 0 }}>
            <Box
              component={RouterLink}
              to="/"
              sx={{ display: 'flex', alignItems: 'center', gap: 1, textDecoration: 'none' }}
            >
              <SolarPowerIcon sx={{ color: 'primary.main', fontSize: 32 }} />
              <Typography
                variant="h6"
                component="div"
                sx={{
                  fontWeight: 'bold',
                  color: 'primary.main',
                  fontSize: '1.25rem',
                }}
              >
                Site Analyzer
              </Typography>
            </Box>
            <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1, ml: 4 }}>
              <Button 
                variant="text" 
                color="info" 
                size="small" 
                onClick={() => scrollToSection('features')}
              >
                Features
              </Button>
              <Button 
                variant="text" 
                color="info" 
                size="small" 
                onClick={() => scrollToSection('highlights')}
              >
                How it Works
              </Button>
              <Button 
                variant="text" 
                color="info" 
                size="small" 
                onClick={() => scrollToSection('faq')}
              >
                FAQ
              </Button>
            </Box>
          </Box>
          <Box
            sx={{
              display: { xs: 'none', md: 'flex' },
              gap: 1,
              alignItems: 'center',
            }}
          >
            <Button
              color="primary"
              variant="outlined"
              size="small"
              sx={{
                borderRadius: 2,
                px: 2,
                py: 0.5,
                fontWeight: 500,
                textTransform: 'none',
                '&:hover': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                },
              }}
              onClick={() => navigate({ to: '/sign-in' })}
            >
              Sign in
            </Button>
            <ColorModeIconDropdown />
          </Box>
          <Box sx={{ display: { md: 'none' }, gap: 1 }}>
            <ColorModeIconDropdown size="medium" />
            <IconButton aria-label="Menu button" onClick={toggleDrawer(true)}>
              <MenuIcon />
            </IconButton>
            <Drawer
              anchor="top"
              open={open}
              onClose={toggleDrawer(false)}
              PaperProps={{
                sx: {
                  top: 'var(--template-frame-height, 0px)',
                },
              }}
            >
              <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SolarPowerIcon sx={{ color: 'primary.main', fontSize: 24 }} />
                    <Typography
                      variant="h6"
                      component="div"
                      sx={{
                        fontWeight: 'bold',
                        color: 'primary.main',
                      }}
                    >
                      Site Analyzer
                    </Typography>
                  </Box>
                  <IconButton onClick={toggleDrawer(false)}>
                    <CloseRoundedIcon />
                  </IconButton>
                </Box>
                <Divider sx={{ my: 3 }} />
                <MenuItem>
                  <Button 
                    variant="text" 
                    color="info" 
                    fullWidth 
                    onClick={() => scrollToSection('features')}
                  >
                    Features
                  </Button>
                </MenuItem>
                <MenuItem>
                  <Button 
                    variant="text" 
                    color="info" 
                    fullWidth 
                    onClick={() => scrollToSection('highlights')}
                  >
                    How it Works
                  </Button>
                </MenuItem>
                <MenuItem>
                  <Button 
                    variant="text" 
                    color="info" 
                    fullWidth 
                    onClick={() => scrollToSection('faq')}
                  >
                    FAQ
                  </Button>
                </MenuItem>
                <Divider sx={{ my: 3 }} />
                <MenuItem>
                  <Button
                    color="primary"
                    variant="outlined"
                    fullWidth
                    sx={{
                      borderRadius: 2,
                      py: 1,
                      fontWeight: 500,
                      textTransform: 'none',
                      '&:hover': {
                        backgroundColor: 'primary.main',
                        color: 'primary.contrastText',
                      },
                    }}
                    onClick={() => {
                      navigate({ to: '/sign-in' });
                      setOpen(false);
                    }}
                  >
                    Sign in
                  </Button>
                </MenuItem>
              </Box>
            </Drawer>
          </Box>
        </StyledToolbar>
      </Container>
    </AppBar>
  );
}
