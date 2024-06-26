import React, {useState, useEffect} from 'react';
import routes from '../../routes/sidebar';
import { NavLink, Route } from 'react-router-dom';
import * as Icons from '../../icons';
import SidebarSubmenu from './SidebarSubmenu';

function Icon({ icon, ...props }) {
  const IconComponent = Icons[icon];
  return <IconComponent {...props} />;
}


function SidebarContent() {
  const [leagueName, setLeagueName] = useState('');
  const [season, setSeason] = useState('');
  
  useEffect(() => {
    const leagueId = '978439391255322624'
    const fetchLeagueData = async () => {
      const response = await fetch(`https://api.sleeper.app/v1/league/${leagueId}`);
      if (!response.ok) {
        console.error(`Error fetching league data: ${response.statusText}`);
        return;
      }
      const data = await response.json();
      setLeagueName(data.name);
      setSeason(data.season);
    };
    fetchLeagueData();
  }, []);

  return (
    <div className="py-4 text-gray-500 dark:text-gray-400">
      <a className="ml-6 text-lg font-bold text-gray-800 dark:text-gray-200" href="#">
        {leagueName} ({season})
      </a>
      <ul className="mt-6">
        {routes.map((route) =>
          route.routes ? (
            <SidebarSubmenu route={route} key={route.name} />
          ) : (
            <li className="relative px-6 py-3" key={route.name}>
              {route.external ? (
                // Render anchor tag for external links
                <a
                  href={route.path}
                  className="inline-flex items-center w-full text-sm font-semibold transition-colors duration-150 hover:text-gray-800 dark:hover:text-gray-200"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Icon className="w-5 h-5" aria-hidden="true" icon={route.icon} />
                  <span className="ml-4">{route.name}</span>
                </a>
              ) : (
                // Render NavLink for internal links
                <NavLink
                  exact
                  to={route.path}
                  className="inline-flex items-center w-full text-sm font-semibold transition-colors duration-150 hover:text-gray-800 dark:hover:text-gray-200"
                  activeClassName="text-gray-800 dark:text-gray-100"
                >
                  <Route path={route.path} exact={route.exact}>
                    <span
                      className="absolute inset-y-0 left-0 w-1 bg-purple-600 rounded-tr-lg rounded-br-lg"
                      aria-hidden="true"
                    ></span>
                  </Route>
                  <Icon className="w-5 h-5" aria-hidden="true" icon={route.icon} />
                  <span className="ml-4">{route.name}</span>
                </NavLink>
              )}
            </li>
          )
        )}
      </ul>
    </div>
  );
}

export default SidebarContent;
