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
import MapDetails from './crud-dashboard/components/MapDetails'
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
  component: MapDetails,
})

const newMapRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'new-map',
  component: NewMap,
})

const usersRoute = createRoute({
  getParentRoute: () => dashboardLayoutRoute,
  path: 'users',
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
  beforeLoad: () => {
    if (!isAdmin()) {
      throw redirect({ to: '/dashboard/welcome' })
    }
  },
  component: Tasks,
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

export default function App() {
  return <RouterProvider router={router} />
}