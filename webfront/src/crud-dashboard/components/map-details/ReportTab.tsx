import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import Collapse from '@mui/material/Collapse';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import Divider from '@mui/material/Divider';
import Button from '@mui/material/Button';

interface ReportTabProps {
  // minimal props for now; will extend when implementing
  mapTaskId?: number | string;
}

const sampleSuitabilityFactors = [
  { key: 'slope', title: 'Slope', description: 'Slope in degrees. Lower is preferable.' },
  { key: 'distance_roads', title: 'Distance to roads', description: 'Distance to nearest road. Closer may be better for access.' },
  { key: 'land_cover', title: 'Land cover', description: 'Categorical land cover suitability scores.' },
];

const sampleRestrictedFactors = [
  { key: 'protected_areas', title: 'Protected areas' },
  { key: 'water_bodies', title: 'Water bodies' },
];

const SectionPaper: React.FC<React.PropsWithChildren<{ id?: string; title: string }>> = ({ id, title, children }) => (
  <Paper id={id} variant="outlined" sx={{ p: 2, mb: 2 }}>
    <Typography variant="h6" sx={{ mb: 1 }}>{title}</Typography>
    {children}
  </Paper>
);

const MapPlaceholder: React.FC<{ caption?: string }> = ({ caption }) => (
  <Box sx={{ border: '1px dashed', borderColor: 'divider', borderRadius: 1, height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'background.paper' }}>
    <Typography color="text.secondary">Map placeholder</Typography>
    {caption && <Typography variant="caption" sx={{ position: 'absolute', bottom: 8 }}>{caption}</Typography>}
  </Box>
);

const ReportTab: React.FC<ReportTabProps> = ({ mapTaskId }) => {
  const [suitOpen, setSuitOpen] = useState<boolean>(false);
  return (
    <Box sx={{ p: 2 }}>
      {/* Outline / Table of contents */}
      <SectionPaper id="report-overview" title="Outline / Contents">
        <List>
          <ListItem disablePadding>
            <ListItemButton component="a" href="#overall">
              <ListItemText primary="Overall summary" />
            </ListItemButton>
          </ListItem>

          {/* Suitability with collapsible child items */}
          <ListItem disablePadding>
            <ListItemButton onClick={() => setSuitOpen(prev => !prev)} sx={{ '&.MuiButtonBase-root': { bgcolor: suitOpen ? 'action.selected' : 'inherit' } }}>
              <ListItemText
                primary={
                  <Typography
                    component="a"
                    href="#suitability"
                    onClick={(e) => e.stopPropagation()}
                    sx={{ textDecoration: 'none', color: suitOpen ? 'primary.main' : 'inherit' }}
                  >
                    Suitability scoring
                  </Typography>
                }
              />
              {suitOpen ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
          </ListItem>
          <Collapse in={suitOpen} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {sampleSuitabilityFactors.map(f => (
                <ListItem key={`toc-${f.key}`} disablePadding>
                  <ListItemButton component="a" href={`#suitability-${f.key}`} sx={{ pl: 6 }}>
                    <ListItemText primary={f.title} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Collapse>

          <ListItem disablePadding>
            <ListItemButton component="a" href="#restrictions">
              <ListItemText primary="Restrictions" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton component="a" href="#final">
              <ListItemText primary="Final" />
            </ListItemButton>
          </ListItem>
        </List>
      </SectionPaper>

      {/* Overall summary */}
      <SectionPaper id="overall" title="Overall summary">
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 2 }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              This report summarizes the processing steps and outputs for task ID: {mapTaskId ?? 'N/A'}. 
              It includes {sampleSuitabilityFactors.length} suitability factors and {sampleRestrictedFactors.length} restricted factors.
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Button size="small" variant="outlined" href="#suitability">Jump to Suitability Scoring</Button>
            </Box>
          </Box>
          <Box>
            <Paper variant="outlined" sx={{ p: 1 }}>
              <Typography variant="subtitle2">Quick stats</Typography>
              <Divider sx={{ my: 1 }} />
              <Typography variant="body2">Suitability factors: {sampleSuitabilityFactors.length}</Typography>
              <Typography variant="body2">Restricted factors: {sampleRestrictedFactors.length}</Typography>
            </Paper>
          </Box>
        </Box>
      </SectionPaper>

      {/* Suitability Scoring */}
      <SectionPaper id="suitability" title="Suitability Scoring">
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          The Suitability Scoring section breaks down each suitability factor into its own subsection with
          description, user-defined scoring rules, and a visualization of the corresponding layer.
        </Typography>

        {sampleSuitabilityFactors.map((f) => (
          <Paper id={`suitability-${f.key}`} key={f.key} variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>{f.title}</Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '7fr 5fr' }, gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">{f.description}</Typography>
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption">User-defined scoring rules (placeholder)</Typography>
                  <Typography variant="body2" sx={{ mt: 1 }} color="text.secondary">{"e.g. slope < 5 -> score 1.0; slope 5-15 -> 0.5; >15 -> 0.0"}</Typography>
                </Box>
              </Box>
              <Box>
                <MapPlaceholder caption={f.title} />
              </Box>
            </Box>
          </Paper>
        ))}

        {/* Aggregation / Sum subsection */}
        <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" sx={{ mb: 1 }}>Aggregated suitability (weighted sum)</Typography>
          <Typography variant="body2" color="text.secondary">This subsection shows how individual suitability factors are combined using weights to compute an aggregated suitability score.</Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2">Weights (example)</Typography>
            <List>
              {sampleSuitabilityFactors.map(f => (
                <ListItem key={f.key} disablePadding>
                  <ListItemText primary={`${f.title}: weight = 0.33 (placeholder)`} />
                </ListItem>
              ))}
            </List>
          </Box>
          <Box sx={{ mt: 2 }}>
            <MapPlaceholder caption="Aggregated suitability map" />
          </Box>
        </Paper>
      </SectionPaper>

      {/* Restrictions */}
      <SectionPaper id="restrictions" title="Restrictions">
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Restricted factors represent areas where development is not allowed or strongly discouraged. The following restricted layers are considered together.
        </Typography>
        <Box sx={{ mb: 2 }}>
          <List>
            {sampleRestrictedFactors.map(r => (
              <ListItem key={r.key} disablePadding>
                <ListItemText primary={r.title} />
              </ListItem>
            ))}
          </List>
        </Box>
        <MapPlaceholder caption="Combined restrictions map" />
      </SectionPaper>

      {/* Final */}
      <SectionPaper id="final" title="Final result">
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          The final map applies the aggregated suitability map and excludes restricted areas. Different colours indicate suitability tiers (e.g., high/medium/low), or masked-out restricted areas.
        </Typography>
        <MapPlaceholder caption="Final suitability map (aggregated & masked)" />
      </SectionPaper>
    </Box>
  );
};

export default ReportTab;
