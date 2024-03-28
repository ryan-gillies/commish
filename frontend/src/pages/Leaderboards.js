import React, { useState } from 'react';
import PageTitle from '../components/Typography/PageTitle';
import SectionTitle from '../components/Typography/SectionTitle';
import LeaderboardCard from '../components/Cards/LeaderboardCard';

function Leaderboards() {
  const [selectedCard, setSelectedCard] = useState(null);

  const handleCardClick = (id) => {
    setSelectedCard(id === selectedCard ? null : id); // Toggle selection
  };

  // Sample card data

  const oneWeekCards = [
    {
      title: 'Sample Card 1',
      lines: [
        { user: 'Ryan ', week: '1', value: '100' },
        { user: 'Tom', week: '3', value: '50' },
      ],
      id: 1,
    },
    {
      title: 'Sample Card 2',
      lines: [
        { user: 'Ryan ', week: '1', value: '100' },
        { user: 'Tom', week: '3', value: '50' },
      ],
      id: 2,
    },
    {
      title: 'Sample Card 3',
      lines: [
        { user: 'Ryan ', week: '1', value: '100' },
        { user: 'Tom', week: '3', value: '50' },
      ],
      id: 3,
    },
    {
      title: 'Sample Card 4',
      lines: [
        { user: 'Ryan ', week: '1', value: '100' },
        { user: 'Tom', week: '3', value: '50' },
      ],
      id: 4,
    },
  ];


  return (
    <>
      <PageTitle>Leaderboards</PageTitle>

      <SectionTitle>One Week Highs</SectionTitle>

      <div className="grid gap-6 mb-8 md:grid-cols-2 xl:grid-cols-4">
        {oneWeekCards.map((card) => (
          <LeaderboardCard
            key={card.id}
            title={card.title}
            lines={card.lines}
            selected={selectedCard === card.id}
            onClick={() => handleCardClick(card.id)}
          >
          </LeaderboardCard>
        ))}
      </div>
      <SectionTitle>Season Cumulatives</SectionTitle>
    </>
  );
}

export default Leaderboards;
