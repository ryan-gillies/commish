import React from 'react';
import { Card, CardBody } from '@windmill/react-ui';

function LeaderboardCard({ title, lines, selected, onClick }) {
  return (
    <Card className={selected ? 'bg-blue-200' : ''} onClick={onClick}>
      {/* Title with padding */}
      <p className="text-lg font-semibold mb-2 text-center pt-4 text-gray-700 dark:text-gray-200">{title}</p>
      <CardBody className="flex flex-col">
        {/* Render each row */}
        {lines.map(({ user, week, value }, index) => (
          <div key={index} className="flex items-center">
            <div className="flex items-center flex-1 ml-4">
              <p className="text-md font-medium text-gray-600 dark:text-gray-100">{user}</p>
            </div>
            <div className="flex items-center flex-1 ml-4">
              <p className="text-md font-medium text-gray-600 dark:text-gray-100">Week {week}</p>
            </div>
            <div className="flex items-center flex-1 justify-end ml-4">
              <p className="text-md font-medium text-gray-600 dark:text-gray-100">{value}</p>
            </div>
          </div>
        ))}
      </CardBody>
    </Card>
  );
}

export default LeaderboardCard;
