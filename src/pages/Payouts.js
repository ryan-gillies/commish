import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import PageTitle from '../components/Typography/PageTitle';
import {
  Table,
  TableHeader,
  TableCell,
  TableBody,
  TableRow,
  TableFooter,
  TableContainer,
  Select,
  Label,
  Pagination,
} from '@windmill/react-ui';
import { Icon } from '@iconify/react';
import arrowDown from '@iconify/icons-heroicons-solid/arrow-down';
import { Bar } from 'react-chartjs-2';
import ChartCard from '../components/Chart/ChartCard'

function PayoutDetails() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const [seasons, setSeasons] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState(searchParams.get('season'));
  const [selectedUser, setSelectedUser] = useState(searchParams.get('username'));

  const [pageTable, setPageTable] = useState(1);
  const [dataTable, setDataTable] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [sortBy, setSortBy] = useState('amount');
  const [sortDirection, setSortDirection] = useState('desc');
  const [totalResults, setTotalResults] = useState(0);
  const resultsPerPage = 10;

  function onPageChangeTable(p) {
    setPageTable(p);
  }

  useEffect(() => {
    async function fetchSeasons() {
      try {
        const response = await fetch(`/api/v1/leagues/seasons`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setSeasons(data);
      } catch (error) {
        console.error('Error fetching seasons:', error);
      }
    }

    fetchSeasons();
  }, []);

  useEffect(() => {
    async function fetchUsers() {
      try {
        const response = await fetch(`/api/v1/users`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setUsers(data);
      } catch (error) {
        console.error('Error fetching seasons:', error);
      }
    }

    fetchUsers();
  }, []);


  useEffect(() => {
    async function fetchPayouts() {
      try {
        let url = '/api/v1/payouts/';
        if (selectedSeason) {
          url = `/api/v1/payouts/${selectedSeason}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();

        const usernames = [...new Set(data.map((payout) => payout.name))];
        const poolTypes = [...new Set(data.map((payout) => payout.pool_type))];
        const poolTypeColors = {
          'main': '#7e3af2',
          'side': '#0694a2',
        };

        // Initialize an empty object to hold aggregated payouts for each user
        const userPayouts = {};

        // Loop through each user and pool type to aggregate payouts
        usernames.forEach(name => {
          // Initialize an empty array to hofld payouts for the current user
          userPayouts[name] = [];

          // Loop through each pool type to aggregate payouts for the current user
          poolTypes.sort();
          poolTypes.forEach(poolType => {
            // Filter payouts for the current user and pool type
            const payoutsForUserAndType = data.filter(payout => payout.name === name && payout.pool_type === poolType);
            // Sum up the payouts for the current user and pool type
            const totalPayoutForUserAndType = payoutsForUserAndType.reduce((sum, payout) => sum + payout.amount, 0);
            // Push the total payout for the current user and pool type to the array
            userPayouts[name].push(totalPayoutForUserAndType);
          });
        });

        // Sort the usernames based on total payout amount
        usernames.sort((a, b) => {
          const totalPayoutA = userPayouts[a].reduce((sum, amount) => sum + amount, 0);
          const totalPayoutB = userPayouts[b].reduce((sum, amount) => sum + amount, 0);
          return totalPayoutB - totalPayoutA;
        });

        // Create datasets for each pool type
        const datasets = poolTypes.map((type) => {
          return {
            label: type,
            data: usernames.map((username) => userPayouts[username][poolTypes.indexOf(type)]),
            backgroundColor: poolTypeColors[type],
            stack: 'stack',
          };
        });

        const chartData = {
          labels: usernames,
          datasets,
        };

        setChartData(chartData);
      } catch (error) {
        console.error('Error fetching payouts:', error);
      }
    }
    fetchPayouts().catch(console.error); // Log any errors thrown
  }, [selectedSeason]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    tooltips: {
      callbacks: {
        label: function (tooltipItem, data) {
          let value = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
          // Format the value as currency with $#,###.##
          return value.toLocaleString('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
          });
        }
      }
    },
    scales: {
      xAxes: [
        {
          stacked: true,
        }
      ],
      yAxes: [
        {
          ticks: {
            beginAtZero: true,
            userCallback: function (value, index, values) {
              return value.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 });
            }
          }
        }
      ],
    },
  };

  const handleBarClick = (event, chartElements) => {
    if (chartElements.length > 0) {
      const clickedIndex = chartElements[0].index;
      const clickedUsername = chartData.labels[clickedIndex];
      setSelectedUser(clickedUsername); // Update selectedUser state
    }
  };

  // Function to handle dropdown change event
  const handleUserDropdownChange = (e) => {
    setSelectedUser(e.target.value); // Update selectedUser state
  };

  useEffect(() => {
    async function fetchPayoutDetails() {
      try {
        let url = '/api/v1/payoutdetails';

        if (selectedSeason && selectedUser) {
          url += `?season=${selectedSeason}&username=${selectedUser}`;
        } else if (selectedSeason) {
          url += `?season=${selectedSeason}`;
        } else if (selectedUser) {
          url += `?username=${selectedUser}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        setDataTable(data);
        setTotalResults(data.length);
        setPageTable(1);
      } catch (error) {
        console.error('Error fetching payouts:', error);
      }
    }

    fetchPayoutDetails();
  }, [selectedSeason, selectedUser]);



  const sortedData = [...dataTable];
  if (sortBy) {
    sortedData.sort((a, b) => {
      const valA = a[sortBy];
      const valB = b[sortBy];
      if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }

  const startIndex = (pageTable - 1) * resultsPerPage;
  const endIndex = Math.min(startIndex + resultsPerPage, totalResults);
  const paginatedData = sortedData.slice(startIndex, endIndex);

  function formatAmount(amount) {
    // Format the amount as currency with $#,###.##
    return amount.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  return (
    <>
      <PageTitle>Payouts</PageTitle>

      {/* Dropdown to select season */}
      <div style={{ marginBottom: '20px' }}>
        <Label>
          <strong>Season</strong>
          <Select
            className="mb-4"
            value={selectedSeason}
            onChange={(e) => setSelectedSeason(e.target.value)}
          >
            <option value="">All-Time</option>
            {seasons.map((season) => (
              <option key={season} value={season}>
                {season}
              </option>
            ))}
          </Select>
        </Label>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <ChartCard title="Payouts">
          <Bar data={chartData}
            options={chartOptions}
            getElementAtEvent={(event, chartElements) => handleBarClick(event, chartElements)}
          />
        </ChartCard>
      </div>
      {/* Dropdown to select user */}
      <div style={{ marginBottom: '20px' }}>
        <Label>
          <strong>User</strong>
          <Select
            className="mb-4"
            value={selectedUser}
            onChange={handleUserDropdownChange} // Call handleUserDropdownChange on change
          >
            <option value="">All Users</option>
            {users.map((user) => (
              <option key={user.username} value={user.username}>
                {user.name}
              </option>
            ))}
          </Select>
        </Label>
      </div>


      <TableContainer className="mb-8">
        <Table>
          <TableHeader>
            <tr>
              <TableCell
                className="cursor-pointer"
                onClick={() => {
                  setSortBy('username');
                  setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                }}
              >
                <div className="flex items-center">
                  User
                  {sortBy === 'username' && (
                    <Icon
                      className={`ml-1 transform ${sortDirection === 'asc' ? 'rotate-180' : ''}`}
                      icon={arrowDown}
                    />
                  )}
                </div>
              </TableCell>
              <TableCell
                className="cursor-pointer"
                onClick={() => {
                  setSortBy('pool');
                  setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                }}
              >
                <div className="flex items-center">
                  Pool
                  {sortBy === 'pool' && (
                    <Icon
                      className={`ml-1 transform ${sortDirection === 'asc' ? 'rotate-180' : ''}`}
                      icon={arrowDown}
                    />
                  )}
                </div>
              </TableCell>
              <TableCell
                className="cursor-pointer"
                onClick={() => {
                  setSortBy('season');
                  setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                }}
              >
                <div className="flex items-center">
                  Season
                  {sortBy === 'season' && (
                    <Icon
                      className={`ml-1 transform ${sortDirection === 'asc' ? 'rotate-180' : ''}`}
                      icon={arrowDown}
                    />
                  )}
                </div>
              </TableCell>
              <TableCell
                className="cursor-pointer"
                onClick={() => {
                  setSortBy('week');
                  setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                }}
              >
                <div className="flex items-center">
                  Week
                  {sortBy === 'week' && (
                    <Icon
                      className={`ml-1 transform ${sortDirection === 'asc' ? 'rotate-180' : ''}`}
                      icon={arrowDown}
                    />
                  )}
                </div>
              </TableCell>
              <TableCell
                className="cursor-pointer"
                onClick={() => {
                  setSortBy('amount');
                  setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                }}
              >
                <div className="flex items-center">
                  Amount
                  {sortBy === 'amount' && (
                    <Icon
                      className={`ml-1 transform ${sortDirection === 'asc' ? 'rotate-180' : ''}`}
                      icon={arrowDown}
                    />
                  )}
                </div>
              </TableCell>
            </tr>
          </TableHeader>
          <TableBody>
            {paginatedData.map((payout, i) => (
              <TableRow key={i}>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-medium">{payout.name}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-medium">{payout.pool}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-medium">{payout.season}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-medium">{payout.week}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-medium">{formatAmount(payout.amount)}</p>
                    </div>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {/* Pagination component */}
        <TableFooter>
          {totalResults > resultsPerPage && (
            <Pagination
              totalResults={totalResults}
              resultsPerPage={resultsPerPage}
              onChange={onPageChangeTable}
              currentPage={pageTable}
              label="Table navigation"
            />
          )}
        </TableFooter>

      </TableContainer>
    </>
  );
}

export default PayoutDetails;
