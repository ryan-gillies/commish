import React, { lazy } from 'react'
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom'
import AccessibleNavigationAnnouncer from './components/AccessibleNavigationAnnouncer'
import PayoutDetails from './pages/Payouts'

const Layout = lazy(() => import('./containers/Layout'))

function App() {
  return (
    <>
      <Router>
        <AccessibleNavigationAnnouncer />
        <Switch>
          <Route path="/" component={Layout} />
          <Redirect from="" to="/app/dashboard" />
          <Redirect from="/" to="/app/dashboard" />
          {/* If you have an index page, you can remothis Redirect */}
        </Switch>
      </Router>
    </>
  )
}

export default App
