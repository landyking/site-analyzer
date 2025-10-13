import {
  RouterProvider,
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  redirect,
} from '@tanstack/react-router'

import SiteAnalyzerHomePage from './marketing-page/SiteAnalyzerHomePage'
import SignIn from './sign-in/SignIn'
import SignUp from './sign-up/SignUp'
import CrudDashboard from './crud-dashboard/CrudDashboard'
import DashboardLayout from './crud-dashboard/components/DashboardLayout'
import Welcome from './crud-dashboard/components/Welcome'
import MyMaps from './crud-dashboard/components/MyMaps'
import {UserMapDetails,AdminMapDetails} from './crud-dashboard/components/MapDetails'
import NewMap from './crud-dashboard/components/NewMap'
import Users from './crud-dashboard/components/Users'
import Tasks from './crud-dashboard/components/Tasks'
import { getAccessToken, isAdmin, isLoggedIn } from './utils/auth'

// Root route renders an Outlet for child routes
const rootRoute = createRootRoute({
  component: () => <Outlet />,
})

// Child routes
const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: SiteAnalyzerHomePage,
})

const signInRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/sign-in',
  /**
   * Redirects to dashboard if user is already logged in.
   */
  beforeLoad: () => {
    if (isLoggedIn()) {
      throw redirect({ to: '/dashboard' })
    }
  },
  component: SignIn,
})

const signUpRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/sign-up',
  component: SignUp,
})

const dashboardRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/dashboard',
  /**
   * Protects the dashboard route by requiring authentication.
   */
  beforeLoad: () => {
    // Protect the dashboard route: require an access token in localStorage
  const token = typeof window !== 'undefined' ? getAccessToken() : null
    if (!token) {
      throw redirect({ to: '/sign-in' })
    }
  },
  component: CrudDashboard,
})

// Dashboard children routes use DashboardLayout with an Outlet
const dashboardLayoutRoute = createRoute({
  getParentRoute: () => dashboardRoute,
  id: 'dashboard-layout',
  component: DashboardLayout,
})

const welcomeRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'welcome',
  component: Welcome,
})

const myMapsRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'my-maps',
  component: MyMaps,
})

const mapDetailsRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'my-maps/$taskId',
  component: UserMapDetails,
})

const newMapRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'new-map',
  component: NewMap,
})

const usersRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'users',
  /**
   * Restricts access to admin users only.
   */
  beforeLoad: () => {
    if (!isAdmin()) {
      throw redirect({ to: '/dashboard/welcome' })
    }
  },
  component: Users,
})

const tasksRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'tasks',
  /**
   * Restricts access to admin users only.
   */
  beforeLoad: () => {
    if (!isAdmin()) {
      throw redirect({ to: '/dashboard/welcome' })
    }
  },
  component: Tasks,
})
const adminMapDetailsRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'tasks/$taskId',
  /**
   * Restricts access to admin users only.
   */
  beforeLoad: () => {
    if (!isAdmin()) {
      throw redirect({ to: '/dashboard/welcome' })
    }
  },
  component: AdminMapDetails,
})

// Index route for /dashboard -> Welcome
const dashboardIndexRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: '/',
  component: Welcome,
})

const routeTree = rootRoute.addChildren([
  homeRoute,
  signInRoute,
  signUpRoute,
  dashboardRoute.addChildren([
    dashboardLayoutRoute.addChildren([
      dashboardIndexRoute,
      welcomeRoute,
      myMapsRoute,
      mapDetailsRoute,
      newMapRoute,
      usersRoute,
      tasksRoute,
      adminMapDetailsRoute
    ]),
  ]),
])

const router = createRouter({
  routeTree,
})

// Type augmentation for router (improves TS DX)
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

/**
 * Main application component that provides routing.
 * @returns The router provider component.
 */
export default function App() {
  return <RouterProvider router={router} />
}