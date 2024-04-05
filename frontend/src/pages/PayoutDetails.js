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

function PayoutDetails() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const [seasons, setSeasons] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState(searchParams.get('season'));
  const [selectedUser, setSelectedUser] = useState(searchParams.get('username'));

  const [pageTable, setPageTable] = useState(1);
  const [dataTable, setDataTable] = useState([]);
  const [sortBy, setSortBy] = useState('amount');
  const [sortDirection, setSortDirection] = useState('desc');
  const [totalResults, setTotalResults] = useState(0);
  const resultsPerPage = 12;
  const history = useHistory();

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(`/api/v1/payouts/seasons`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setSeasons(data);
      } catch (error) {
        console.error('Error fetching seasons:', error);
      }
    }

    fetchData();
  }, []);

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    queryParams.set('season', selectedSeason);
    queryParams.set('username', selectedUser);
    history.push({ search: queryParams.toString() });
  }, [selectedSeason, selectedUser, history, location.search]);

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
      } catch (error) {
        console.error('Error fetching payout details:', error);
      }
    }

    fetchPayoutDetails();
  }, [selectedSeason, selectedUser]);

  function onPageChangeTable(p) {
    setPageTable(p);
  }

  const startIndex = (pageTable - 1) * resultsPerPage;
  const endIndex = Math.min(startIndex + resultsPerPage, totalResults);
  const paginatedData = dataTable.slice(startIndex, endIndex);

  // Sorting Logic
  const sortedData = [...paginatedData];
  if (sortBy) {
    sortedData.sort((a, b) => {
      const valA = a[sortBy];
      const valB = b[sortBy];
      if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }

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
      <PageTitle>Payout Details</PageTitle>

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

      {/* Dropdown to select user */}
      <div style={{ marginBottom: '20px' }}>
        <Label>
          <strong>User</strong>
          <Select
            className="mb-4"
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
          >
            <option value="rgillies28">rgillies28</option>
            <option value="ChristianSwagner">ChristianSwagner</option>
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
            {sortedData.map((payout, i) => (
              <TableRow key={i}>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-semibold">{payout.username}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-semibold">{payout.pool}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-semibold">{payout.season}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <div>
                      <p className="font-semibold">{payout.week}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="text-sm">{formatAmount(payout.amount)}</span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {/* Pagination component */}
        <TableFooter>
          <Pagination
            totalResults={sortedData.length}
            resultsPerPage={resultsPerPage}
            onChange={onPageChangeTable}
            label="Table navigation"
          />
        </TableFooter>
      </TableContainer>
    </>
  );
}

export default PayoutDetails;
