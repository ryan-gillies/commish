import React from 'react';
import { Card, CardBody } from '@windmill/react-ui';

function LeaderboardCard({ title, lines, selected, onClick }) {
  
  const headers = lines.reduce((acc, { user, player, position, week, opponent, score, record, points, points_against, net_points }) => {
    if (user) acc.user = true;
    if (player) acc.player = true;
    if (week) acc.week = true;
    if (opponent) acc.opponent = true;
    if (score) acc.score = true;
    if (record) acc.record = true;
    if (points) acc.points = true;
    if (points_against) acc.points_against = true;
    if (net_points) acc.net_points = true;
    if (position) acc.position = true;
    return acc;
  }, {});

  return (
    <Card className={selected ? 'bg-blue-200' : ''} onClick={onClick}>
      {/* Title with padding */}
      <p className="text-lg font-semibold mb-2 text-center pt-4 text-gray-700 dark:text-gray-200">{title}</p>
      <CardBody className="flex flex-col">
        {/* Render headers */}
        <div className="flex items-center">
          {headers.user && (
            <div className="w-2/5 text-left ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100">User</p>
            </div>
          )}
          {headers.player && (
            <div className="w-2/5 text-left ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100">Player</p>
            </div>
          )}
          {headers.position &&(
            <div className="w-1/5 text-left ml-4">
            <p className="text-sm font-bold text-gray-600 dark:text-gray-100">Position</p>
          </div>          )}
          {headers.opponent && (
            <div className="w-2/5 text-left ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100">Opponent</p>
            </div>
          )}
          {headers.week && (
            <div className="w-1/5 text-left ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100">Week</p>
            </div>
          )}
          {headers.score && (
            <div className="w-1/5 text-center ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100"></p>
            </div>
          )}
          {headers.record && (
            <div className="w-1/5 text-center ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100">Record</p>
            </div>
          )}
          {headers.points && (
            <div className="w-1/5 text-center ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100">Pts For</p>
            </div>
          )}
          {headers.points_against && (
            <div className="w-1/5 text-center ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100">Pts Against</p>
            </div>
          )}
          {headers.net_points && (
            <div className="w-1/5 text-center ml-4">
              <p className="text-sm font-bold text-gray-600 dark:text-gray-100">Net Points</p>
            </div>
          )}
        </div>
        {/* Render each row */}
        {lines.map(({ user, player, position, week, opponent, score, record, points, points_against, net_points }, index) => (
          <div key={index} className="flex items-center">
            {user && (
              <div className="w-2/5 text-left ml-4">
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-100">{user}</p>
              </div>
            )}
            {player && (
              <div className="w-2/5 text-left ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{player}</p>
              </div>
            )}
            {position && (
              <div className="w-1/5 text-left ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{position}</p>
              </div>
            )}
            {opponent && (
              <div className="w-2/5 text-left ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{opponent}</p>
              </div>
            )}
            {week && (
              <div className="w-1/5 text-left ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{week}</p>
              </div>
            )}
            {score && (
              <div className="w-1/5 text-right ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{score}</p>
              </div>
            )}
            {record && (
              <div className="w-1/5 text-right ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{record}</p>
              </div>
            )}
            {points && (
              <div className="w-1/5 text-right ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{points}</p>
              </div>
            )}
            {points_against && (
              <div className="w-1/5 text-right ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{points_against}</p>
              </div>
            )}
            {net_points && (
              <div className="w-1/5 text-right ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-100">{net_points}</p>
              </div>
            )}
          </div>
        ))}
      </CardBody>
    </Card>
  );
}

export default LeaderboardCard;
