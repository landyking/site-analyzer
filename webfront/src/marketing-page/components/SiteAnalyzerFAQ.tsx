import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const faqData = [
  {
    id: 'panel1',
    question: 'What types of data does Site Analyzer require for analysis?',
    answer: 'Site Analyzer requires geospatial data including district boundaries, terrain elevation data (DEM), land use information, solar radiation data, temperature data, and infrastructure layers like power lines and roads. We support common GIS formats including Shapefiles, GeoTIFF, and other standard geospatial formats.',
  },
  {
    id: 'panel2',
    question: 'How accurate are the solar site suitability assessments?',
    answer: 'Our analysis accuracy depends on the quality and resolution of input data. With high-quality datasets, our multi-factor analysis provides reliable suitability assessments that consider topography, solar radiation, environmental constraints, and proximity to infrastructure. Results are validated against industry standards and best practices.',
  },
  {
    id: 'panel3',
    question: 'Can I customize the analysis parameters and weighting factors?',
    answer: 'Yes, Site Analyzer allows you to customize analysis parameters including constraint thresholds, weighting factors for different criteria, and scoring methods. You can adjust factors like minimum solar radiation requirements, maximum slope angles, buffer distances from protected areas, and infrastructure proximity weights.',
  },
  {
    id: 'panel4',
    question: 'What file formats are supported for data upload and export?',
    answer: 'We support standard GIS formats for input including Shapefiles (.shp), GeoTIFF (.tif), and other raster/vector formats. Analysis results can be exported as processed shapefiles, raster datasets, PDF reports, and interactive web maps for integration with other GIS software.',
  },
  {
    id: 'panel5',
    question: 'How long does a typical analysis take to complete?',
    answer: 'Analysis time depends on the size of your study area and complexity of datasets. Small to medium districts typically process within 10-30 minutes, while larger regions with high-resolution data may take 1-2 hours. You can monitor progress through our real-time status dashboard.',
  },
  {
    id: 'panel6',
    question: 'Can multiple users collaborate on analysis projects?',
    answer: 'Yes, Site Analyzer supports user authentication and project management. Team members can share analysis tasks, review results, and collaborate on site selection decisions. User permissions can be configured to control access to sensitive data and analysis results.',
  },
];

export default function SiteAnalyzerFAQ() {
  const [expanded, setExpanded] = React.useState<string[]>([]);

  const handleChange =
    (panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
      setExpanded(
        isExpanded
          ? [...expanded, panel]
          : expanded.filter((item) => item !== panel),
      );
    };

  return (
    <Container
      id="faq"
      sx={{
        pt: { xs: 4, sm: 12 },
        pb: { xs: 8, sm: 16 },
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: { xs: 3, sm: 6 },
      }}
    >
      <Typography
        component="h2"
        variant="h4"
        sx={{
          color: 'text.primary',
          width: { sm: '100%', md: '60%' },
          textAlign: { sm: 'left', md: 'center' },
          fontWeight: 'bold',
          mb: 2,
        }}
      >
        Frequently Asked Questions
      </Typography>
      <Typography
        variant="h6"
        sx={{
          color: 'text.secondary',
          width: { sm: '100%', md: '70%' },
          textAlign: { sm: 'left', md: 'center' },
          fontWeight: 300,
          mb: 4,
        }}
      >
        Common questions about solar site analysis and our platform capabilities
      </Typography>
      <Box sx={{ width: '100%', maxWidth: '800px' }}>
        {faqData.map((item) => (
          <Accordion
            key={item.id}
            expanded={expanded.includes(item.id)}
            onChange={handleChange(item.id)}
            sx={{
              mb: 2,
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1,
              '&:before': {
                display: 'none',
              },
              '&.Mui-expanded': {
                margin: '0 0 16px 0',
              },
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls={`${item.id}-content`}
              id={`${item.id}-header`}
              sx={{
                backgroundColor: 'background.paper',
                borderRadius: '4px 4px 0 0',
                '&.Mui-expanded': {
                  borderRadius: '4px 4px 0 0',
                },
              }}
            >
              <Typography 
                component="h3" 
                variant="subtitle2"
                sx={{ 
                  fontWeight: 'medium',
                  color: 'text.primary',
                }}
              >
                {item.question}
              </Typography>
            </AccordionSummary>
            <AccordionDetails
              sx={{
                backgroundColor: 'background.default',
                borderRadius: '0 0 4px 4px',
              }}
            >
              <Typography
                variant="body2"
                gutterBottom
                sx={{ 
                  maxWidth: { sm: '100%', md: '70%' },
                  color: 'text.secondary',
                  lineHeight: 1.6,
                }}
              >
                {item.answer}
              </Typography>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
      <Typography
        variant="body2"
        sx={{ 
          color: 'text.secondary',
          textAlign: 'center',
          mt: 4,
        }}
      >
        Have more questions?{' '}
        <Link href="#" color="primary" sx={{ fontWeight: 'medium' }}>
          Contact our support team
        </Link>{' '}
        for technical assistance and consultation.
      </Typography>
    </Container>
  );
}
