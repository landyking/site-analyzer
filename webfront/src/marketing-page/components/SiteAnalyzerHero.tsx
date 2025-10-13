import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import MapIcon from '@mui/icons-material/Map';
import { Link as RouterLink } from '@tanstack/react-router';

// Import images for carousel
import solarImg from '../../assets/solar.png';
import finalImg from '../../assets/final.png';
import restrictedImg from '../../assets/restricted.png';
import powerlinesImg from '../../assets/powerlines.png';
import roadsImg from '../../assets/roads.png';
import slopeImg from '../../assets/slope.png';
import weightedImg from '../../assets/weighted.png';

// Types
interface CarouselItem {
  image: string;
  title: string;
  description: string;
}

// Carousel data 
const CAROUSEL_ITEMS: CarouselItem[] = [
  { 
    image: solarImg, 
    title: "Solar Potential Map",
    description: "Visualize areas with optimal solar radiation exposure"
  },
  { 
    image: finalImg, 
    title: "Final Suitability Analysis",
    description: "Identify the most suitable sites for solar installations"
  },
  { 
    image: restrictedImg, 
    title: "Restricted Areas",
    description: "Highlight zones with regulatory or environmental constraints"
  },
  { 
    image: powerlinesImg, 
    title: "Power Infrastructure",
    description: "Map proximity to existing electrical grid infrastructure"
  },
  { 
    image: roadsImg, 
    title: "Road Network Access",
    description: "Evaluate site accessibility via transportation networks"
  },
  { 
    image: slopeImg, 
    title: "Terrain Slope Analysis",
    description: "Analyze land gradient impact on installation feasibility"
  },
  { 
    image: weightedImg, 
    title: "Weighted Suitability",
    description: "Combine multiple factors for comprehensive assessment"
  }
];

// Reusable styles
const carouselImageStyles = {
  width: '100%',
  height: '100%',
  objectFit: 'cover',
  objectPosition: 'center',
  position: 'absolute',
  top: 0,
  left: 0,
  zIndex: 1,
  borderRadius: '8px', 
  transition: 'opacity 0.8s ease, transform 0.8s ease',
  animation: 'fadeIn 0.8s ease',
  '@keyframes fadeIn': {
    '0%': {
      opacity: 0.7,
      transform: 'scale(1.05)'
    },
    '100%': {
      opacity: 1,
      transform: 'scale(1)'
    }
  }
};

const navigationArrowBaseStyles = (theme: any) => ({
  position: 'absolute',
  top: '50%',
  transform: 'translateY(-50%)',
  zIndex: 10,
  width: { xs: '28px', sm: '35px' },
  height: { xs: '28px', sm: '35px' },
  borderRadius: '50%',
  backgroundColor: 'rgba(255, 255, 255, 0.2)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  boxShadow: 'none',
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.4)',
    transform: 'translateY(-50%) scale(1.05)',
  },
  ...theme.applyStyles('dark', {
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    '&:hover': {
      backgroundColor: 'rgba(0, 0, 0, 0.4)',
      transform: 'translateY(-50%) scale(1.05)',
    },
  }),
});

// Carousel Navigation component
/**
 * Navigation component for the image carousel with arrows and dots.
 * @param onPrev - Function to go to previous slide.
 * @param onNext - Function to go to next slide.
 * @param currentIndex - Current slide index.
 * @param totalItems - Total number of slides.
 * @param onSelectSlide - Function to select a specific slide.
 * @returns The carousel navigation component.
 */
const CarouselNavigation = ({ 
  onPrev, 
  onNext, 
  currentIndex, 
  totalItems, 
  onSelectSlide 
}: { 
  onPrev: () => void, 
  onNext: () => void, 
  currentIndex: number, 
  totalItems: number,
  onSelectSlide: (index: number) => void
}) => {
  return (
    <>
      {/* Previous arrow */}
      <Box 
        onClick={onPrev}
        sx={(theme) => ({
          ...navigationArrowBaseStyles(theme),
          left: { xs: '10px', sm: '20px' },
          '&::before': {
            content: '""',
            width: '8px',
            height: '8px',
            borderLeft: `2px solid ${theme.palette.primary.main}`,
            borderBottom: `2px solid ${theme.palette.primary.main}`,
            transform: 'rotate(45deg)',
            marginLeft: '4px',
          }
        })}
      />
      
      {/* Next arrow */}
      <Box 
        onClick={onNext}
        sx={(theme) => ({
          ...navigationArrowBaseStyles(theme),
          right: { xs: '10px', sm: '20px' },
          '&::before': {
            content: '""',
            width: '8px',
            height: '8px',
            borderRight: `2px solid ${theme.palette.primary.main}`,
            borderTop: `2px solid ${theme.palette.primary.main}`,
            transform: 'rotate(45deg)',
            marginRight: '4px',
          }
        })}
      />
      
      {/* Dots navigation */}
      <Stack 
        direction="row" 
        spacing={1}
        sx={{ 
          position: 'absolute',
          bottom: { xs: '15px', sm: '20px' },
          left: { xs: '20px', sm: '30px' },
          transform: 'none',
          zIndex: 10,
          display: 'flex',
          justifyContent: 'flex-start',
          backgroundColor: (theme) => theme.palette.mode === 'dark' 
            ? 'rgba(0, 0, 0, 0.15)' 
            : 'rgba(255, 255, 255, 0.15)',
          borderRadius: '20px',
          padding: '3px 6px',
          backdropFilter: 'blur(2px)'
        }}
      >
        {Array.from({ length: totalItems }).map((_, index) => (
          <Box
            key={index}
            onClick={() => onSelectSlide(index)}
            sx={(theme) => ({
              width: { xs: 5, sm: 6 },
              height: { xs: 5, sm: 6 },
              borderRadius: '50%',
              backgroundColor: currentIndex === index 
                ? theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.5)'
                : theme.palette.mode === 'dark' 
                  ? 'rgba(255, 255, 255, 0.2)' 
                  : 'rgba(0, 0, 0, 0.15)',
              cursor: 'pointer',
              transition: 'all 0.3s',
              margin: '0 2px',
              '&:hover': {
                backgroundColor: currentIndex === index 
                  ? theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.6)'
                  : theme.palette.mode === 'dark'
                    ? 'rgba(255, 255, 255, 0.3)'
                    : 'rgba(0, 0, 0, 0.25)',
                transform: 'scale(1.1)',
              },
            })}
          />
        ))}
      </Stack>
    </>
  );
};

// Carousel Description component
/**
 * Description overlay component for carousel items.
 * @param item - The carousel item to display.
 * @returns The description overlay component.
 */
const CarouselDescription = ({ item }: { item: CarouselItem }) => {
  return (
    <Box
      sx={(theme) => ({
        position: 'absolute',
        bottom: { xs: '20px', sm: '30px' },
        right: { xs: '20px', sm: '30px' },
        left: 'auto', 
        transform: 'none', 
        width: { xs: '70%', sm: '50%', md: '40%' },
        backgroundColor: theme.palette.mode === 'dark' 
          ? 'rgba(0, 0, 0, 0.2)' 
          : 'rgba(255, 255, 255, 0.2)',
        backdropFilter: 'blur(4px)',
        borderRadius: '8px',
        padding: { xs: theme.spacing(1.2), sm: theme.spacing(1.5) },
        boxShadow: 'none', 
        textAlign: 'right',
        transition: 'all 0.5s ease',
        zIndex: 10,
        border: '1px solid',
        borderColor: theme.palette.mode === 'dark'
          ? 'rgba(255, 255, 255, 0.05)'
          : 'rgba(255, 255, 255, 0.1)'
      })}
    >
      <Typography
        variant="h6"
        sx={(theme) => ({
          color: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.85)' : 'rgba(0,0,0,0.75)',
          fontWeight: '500',
          fontSize: { xs: '0.9rem', sm: '1rem', md: '1.1rem' },
          mb: 0.5,
          textShadow: 'none', 
          opacity: 0.9,
        })}
      >
        {item.title}
      </Typography>
      <Typography
        variant="body2"
        sx={(theme) => ({
          color: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.6)',
          fontSize: { xs: '0.75rem', sm: '0.8rem', md: '0.85rem' },
          fontWeight: '400',
          opacity: 0.85,
          textShadow: 'none', 
        })}
      >
        {item.description}
      </Typography>
    </Box>
  );
};

// Image carousel component
/**
 * Auto-rotating image carousel with navigation controls.
 * @returns The image carousel component.
 */
const ImageCarousel = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  
  // Auto-rotate carousel
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => 
        prevIndex === CAROUSEL_ITEMS.length - 1 ? 0 : prevIndex + 1
      );
    }, 4000); // Change image every 4 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  /**
   * Handles navigation between carousel slides.
   * @param direction - Direction to navigate ('next' or 'prev').
   */
  const handleNavigation = (direction: 'next' | 'prev') => {
    if (direction === 'next') {
      setCurrentIndex((prevIndex) => 
        prevIndex === CAROUSEL_ITEMS.length - 1 ? 0 : prevIndex + 1
      );
    } else {
      setCurrentIndex((prevIndex) => 
        prevIndex === 0 ? CAROUSEL_ITEMS.length - 1 : prevIndex - 1
      );
    }
  };

  /**
   * Navigates to a specific slide by index.
   * @param index - The slide index to navigate to.
   */
  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  const currentItem = CAROUSEL_ITEMS[currentIndex];
  
  return (
    <Box sx={{ 
      position: 'relative', 
      width: '100%',
      height: '100%', 
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden',
      borderRadius: '8px', 
      border: (theme) => `1px solid ${
        theme.palette.mode === 'dark' 
          ? 'rgba(255, 255, 255, 0.08)'
          : 'rgba(0, 0, 0, 0.05)'
      }`,
      boxShadow: (theme) => theme.palette.mode === 'dark' 
        ? '0 8px 32px rgba(0, 0, 0, 0.3)' 
        : '0 8px 32px rgba(0, 0, 0, 0.1)',
    }}>
      <Box sx={{ 
        width: '100%',
        height: '100%',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 'inherit'
      }}>
        {/* Image and semi-transparent overlay */}
        <Box 
          component="img"
          src={currentItem.image}
          alt={currentItem.title}
          sx={carouselImageStyles}
        />
        
        <Box 
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: (theme) => theme.palette.mode === 'dark' 
              ? 'linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.2))' 
              : 'linear-gradient(rgba(255,255,255,0.05), rgba(255,255,255,0.1))',
            zIndex: 2,
            borderRadius: '8px' 
          }}
        />

        {/* Description */}
        <CarouselDescription item={currentItem} />
      </Box>
      
      {/* Navigation controls */}
      <CarouselNavigation 
        onPrev={() => handleNavigation('prev')}
        onNext={() => handleNavigation('next')}
        currentIndex={currentIndex}
        totalItems={CAROUSEL_ITEMS.length}
        onSelectSlide={goToSlide}
      />
    </Box>
  );
};

// Hero content component
const HeroContent = () => {
  return (
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
      <HeroButtons />
    </Stack>
  );
};

// Hero buttons component
const HeroButtons = () => {
  return (
    <Stack
      direction={{ xs: 'column', sm: 'row' }}
      spacing={2}
      useFlexGap
      sx={{ pt: 3, width: { xs: '100%', sm: 'auto' } }}
    >
      <Button
        component={RouterLink}
        to="/sign-in"
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
        component={RouterLink}
        to="/sign-in"
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
  );
};

// Main component
/**
 * Hero section component for the Site Analyzer homepage with carousel.
 * @returns The hero section component.
 */
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
        <HeroContent />
        <Box 
          sx={{
            width: '100%',
            height: { xs: 400, sm: 500 },
            marginTop: { xs: 6, sm: 8 },
            borderRadius: '8px', 
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <ImageCarousel />
        </Box>
      </Container>
    </Box>
  );
}