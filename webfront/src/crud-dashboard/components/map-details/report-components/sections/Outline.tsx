import React, { useState } from 'react';
// Outline does not render a SectionPaper title; it's a compact TOC
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import type { MapTaskDetails } from '../../../../../client/types.gen';
import { SUITABILITY_LABELS } from '@/crud-dashboard/components/shared/suitability-utils';

interface Props {
  mapTask: MapTaskDetails;
}

const Outline: React.FC<Props> = ({ mapTask }) => {
  const [suitOpen, setSuitOpen] = useState<boolean>(false);
  const suitabilityFactors= mapTask.suitability_factors?.sort((a, b) => b.weight - a.weight) || [];
  return (
    <Box id="report-overview" sx={{ mb: 2 }}>
      <Box sx={{ position: 'relative', display: 'flex', alignItems: 'stretch' }}>
        {/* left accent - flush against the content box */}
        <Box sx={{ width: 4, bgcolor: 'primary.main', borderRadius: '4px 0 0 4px' }} />
        <Box sx={{ flex: 1, bgcolor: 'grey.50', p: 0.5, borderRadius: '0 8px 8px 0', boxShadow: '0 1px 2px rgba(0,0,0,0.02)' }}>
        <List sx={{ py: 0 }} aria-label="report table of contents">
                <ListItem disablePadding sx={{ py: 0.08 }}>
                  <ListItemButton component="a" href="#overall" sx={{ py: 0.18, minHeight: 20 }}>
                    <ListItemText primary={<span style={{ fontSize: '0.9rem' }}>Overall summary</span>} />
                  </ListItemButton>
                </ListItem>

          <ListItem disablePadding sx={{ py: 0.08 }}>
            <ListItemButton onClick={() => setSuitOpen(prev => !prev)} sx={{ py: 0.18, minHeight: 20, '&.MuiButtonBase-root': { bgcolor: suitOpen ? 'action.selected' : 'inherit' } }}>
              <ListItemText
                primary={
                  <a href="#suitability" onClick={(e) => e.stopPropagation()} style={{ textDecoration: 'none', color: suitOpen ? 'var(--mui-palette-primary-main)' : 'inherit', fontSize: '0.9rem' }}>
                    Suitability scoring
                  </a>
                }
              />
              {suitOpen ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
            </ListItemButton>
          </ListItem>

          <Collapse in={suitOpen} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {suitabilityFactors.map(f => (
                <ListItem key={`toc-${f.kind}`} disablePadding sx={{ py: 0.05 }}>
                  <ListItemButton component="a" href={`#suitability-${f.kind}`} sx={{ pl: 2, py: 0.2, minHeight: 20 }}>
                    <ListItemText primary={<span style={{ fontSize: '0.86rem', color: 'var(--mui-palette-text-secondary)' }}>{SUITABILITY_LABELS[f.kind] || f.kind}</span>} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Collapse>

          <ListItem disablePadding sx={{ py: 0.08 }}>
            <ListItemButton component="a" href="#constraints" sx={{ py: 0.25, minHeight: 22 }}>
              <ListItemText primary={<span style={{ fontSize: '0.9rem' }}>Constraints</span>} />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding sx={{ py: 0.08 }}>
            <ListItemButton component="a" href="#final" sx={{ py: 0.25, minHeight: 22 }}>
              <ListItemText primary={<span style={{ fontSize: '0.9rem' }}>Final result</span>} />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Box>
  </Box>
  );
};

export default Outline;
