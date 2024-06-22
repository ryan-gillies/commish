import { lazy } from 'react'

// use lazy for better code splitting, a.k.a. load faster
const Dashboard = lazy(() => import('../pages/Dashboard'))
const Forms = lazy(() => import('../pages/Forms'))
const Leaderboards = lazy(() => import('../pages/Leaderboards'))
const Charts = lazy(() => import('../pages/Charts'))
const PayoutDetails = lazy(() => import('../pages/Payouts'))
const Modals = lazy(() => import('../pages/Modals'))
const Payouts = lazy(() => import('../pages/Payouts'))
const Page404 = lazy(() => import('../pages/404'))

/**
 * ⚠ These are internal routes!
 * They will be rendered inside the app, using the default `containers/Layout`.
 * If you want to add a route to, let's say, a landing page, you should add
 * it to the `App`'s router, exactly like `Login`, `CreateAccount` and other pages
 * are routed.
 *
 * If you're looking for the links rendered in the SidebarContent, go to
 * `routes/sidebar.js`
 */
const routes = [
  {
    path: '/dashboard', // the url
    component: Dashboard, // view rendered
  },
  {
    path: '/forms',
    component: Forms,
  },
  {
    path: '/leaderboards',
    component: Leaderboards,
  },
  {
    path: '/charts',
    component: Charts,
  },
  {
    path: '/payoutdetails',
    component: PayoutDetails,
  },
  {
    path: '/modals',
    component: Modals,
  },
  {
    path: '/payouts',
    component: Payouts,
  },
  {
    path: '/404',
    component: Page404,
  },
]

export default routes
