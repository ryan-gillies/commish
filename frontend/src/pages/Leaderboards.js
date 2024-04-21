import React, { useEffect, useState } from 'react';
import PageTitle from '../components/Typography/PageTitle';
import SectionTitle from '../components/Typography/SectionTitle';
import LeaderboardCard from '../components/Cards/LeaderboardCard';
import selectedSeason from './Payouts';

function Leaderboards() {
  const leagueId = '978439391255322624';

  const [pools, setPools] = useState([]);
  const [selectedCard, setSelectedCard] = useState(null);
  const [leaderboards, setLeaderboards] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/v1/pools');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setPools(data.sort((a, b) => a.label.localeCompare(b.label)));
        setLoading(false);
      } catch (error) {
        console.error('Error fetching pools:', error);
      }
    }
    fetchData();
  }, []);

  useEffect(() => {
    pools.filter(pool => pool.pool_subtype === 'season_high'|| pool.pool_subtype === 'season_cumulative').forEach(async (pool) => {
      try {
        const response = await fetch(`/api/v1/pools/leaderboard?league_id=${leagueId}&pool_id=${pool.pool_id}`);
        if (!response.ok) {
          console.error(`Error fetching leaderboard for pool ${pool.pool_id}: ${response.statusText}`);
          return; // Continue to next pool if error occurs
        }
        const data = await response.json();
        setLeaderboards(prevLeaderboards => ({ ...prevLeaderboards, [pool.pool_id]: data }));
      } catch (error) {
        console.error('Error fetching leaderboards:', error);
      }
    });
  }, [leagueId, pools]);


  // const handleCardClick = (id) => {
  //   setSelectedCard(id === selectedCard ? null : id); // Toggle selection
  // };

  return (
    <>
      <PageTitle>Leaderboards</PageTitle>

      <SectionTitle>Season Highs</SectionTitle>

      <div className="grid gap-6 mb-8 md:grid-cols-2 xl:grid-cols-2">

        {pools
          .filter(pool => pool.pool_subtype === 'season_high')
          .map((pool) => (
            <LeaderboardCard
              key={pool.pool_id}
              title={pool.label}
              lines={leaderboards[pool.pool_id]?.map((entry) => ({
                user: entry.username,
                week: entry.week,
                opponent: entry.opponent,
                player: entry.player_name,
                position: entry.position,
                score: entry.score ? entry.score.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : undefined,
              })) || []}
              selected={selectedCard === pool.pool_id}
              // onClick={() => handleCardClick(pool.pool_id)}
            />
          ))}
      </div>

      <SectionTitle>Season Cumulatives</SectionTitle>
      <div className="grid gap-6 mb-8 md:grid-cols-2 xl:grid-cols-2">

        {pools
          .filter(pool => pool.pool_subtype === 'season_cumulative')
          .map((pool) => (
            <LeaderboardCard
              key={pool.pool_id}
              title={pool.label}
              lines={leaderboards[pool.pool_id]?.map((entry) => ({
                user: entry.username,
                record: entry.total_wins ? `${entry.total_wins}-${entry.total_losses}` : undefined,
                points: entry.total_points_for ? entry.total_points_for.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : undefined,
                points_against: entry.total_points_against ? entry.total_points_against.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : undefined,
                net_points: entry.total_points_for && entry.total_points_against ? (entry.total_points_for - entry.total_points_against).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : undefined,
                player: entry.player_name,
                position: entry.position,
                score: entry.score ? entry.score.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : undefined,
              })) || []}

              selected={selectedCard === pool.pool_id}
              // onClick={() => handleCardClick(pool.pool_id)}
            />
          ))}
      </div>

    </>
  );
}

export default Leaderboards;

