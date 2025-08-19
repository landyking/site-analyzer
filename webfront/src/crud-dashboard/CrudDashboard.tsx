// React import not required with react-jsx runtime
import CssBaseline from '@mui/material/CssBaseline';
import { Outlet } from '@tanstack/react-router';
import NotificationsProvider from './hooks/useNotifications/NotificationsProvider';
import DialogsProvider from './hooks/useDialogs/DialogsProvider';
import AppTheme from '../shared-theme/AppTheme';
import {
  sidebarCustomizations,
  formInputCustomizations,
} from './theme/customizations';
// This component now only provides theming/contexts and renders the layout.
// Routes are defined in App.tsx via @tanstack/react-router under /dashboard.

const themeComponents = {
  ...formInputCustomizations,
  ...sidebarCustomizations
};

export default function CrudDashboard(props: { disableCustomTheme?: boolean }) {
  return (
    <AppTheme {...props} themeComponents={themeComponents}>
      <CssBaseline enableColorScheme />
      <NotificationsProvider>
        <DialogsProvider>
          <Outlet />
        </DialogsProvider>
      </NotificationsProvider>
    </AppTheme>
  );
}
