const routes = [
  {
    path: '/app/dashboard', // the url
    icon: 'HomeIcon', // the component being exported from icons/index.js
    name: 'Dashboard', // name that appear in Sidebar
  },
  {
    icon: 'MoneyIcon',
    name: 'Side Pools',
    routes: [
      // submenu
      {
        path: '/app/payouts',
        icon: 'MoneyIcon',
        name: 'Payouts',
      },
      {
        path: '/app/leaderboards',
        icon: 'TablesIcon',
        name: 'Leaderboards',
      },
    ],
  },
  {
    path: '/app/record_book',
    icon: 'PagesIcon',
    name: 'Record Book',
  },
  {
    external: true,
    path: 'https://sleeper.app',
    icon: 'OutlineLogoutIcon',
    name: 'Go to Sleeper',
  }
]

export default routes
