import {
  RouterProvider,
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
} from '@tanstack/react-router'

import SiteAnalyzerHomePage from './marketing-page/SiteAnalyzerHomePage'
import SignIn from './sign-in/SignIn'
import SignUp from './sign-up/SignUp'

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
  component: SignIn,
})

const signUpRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/sign-up',
  component: SignUp,
})

const routeTree = rootRoute.addChildren([homeRoute, signInRoute, signUpRoute])

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