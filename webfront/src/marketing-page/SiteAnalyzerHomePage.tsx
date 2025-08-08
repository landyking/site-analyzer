import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';
import AppTheme from '../shared-theme/AppTheme';
import SiteAnalyzerAppBar from './components/SiteAnalyzerAppBar';
import SiteAnalyzerHero from './components/SiteAnalyzerHero';
import SiteAnalyzerFeatures from './components/SiteAnalyzerFeatures';
import SiteAnalyzerHighlights from './components/SiteAnalyzerHighlights';
import SiteAnalyzerFAQ from './components/SiteAnalyzerFAQ';
import SiteAnalyzerFooter from './components/SiteAnalyzerFooter';

export default function SiteAnalyzerHomePage(props: { disableCustomTheme?: boolean }) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />

      <SiteAnalyzerAppBar />
      <SiteAnalyzerHero />
      <div>
        <SiteAnalyzerFeatures />
        <Divider />
        <SiteAnalyzerHighlights />
        <Divider />
        <SiteAnalyzerFAQ />
        <Divider />
        <SiteAnalyzerFooter />
      </div>
    </AppTheme>
  );
}
