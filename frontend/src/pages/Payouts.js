import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import PageTitle from '../components/Typography/PageTitle';
import {
  Table,
  TableHeader,
  TableCell,
  TableBody,
  TableRow,
  TableFooter,
  TableContainer,
  Avatar,
  Button,
  Pagination,
  Select,
  Label
} from '@windmill/react-ui';
import { Icon } from '@iconify/react';
import arrowDown from '@iconify/icons-heroicons-solid/arrow-down';



function Payouts() {
  const [pageTable, setPageTable] = useState(1);
  const [dataTable, setDataTable] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState('');
  const [seasons, setSeasons] = useState([]);
  const history = useHistory();
  const [totalResults, setTotalResults] = useState(0);
  const [sortBy, setSortBy] = useState('amount');
  const [sortDirection, setSortDirection] = useState('desc');
  const resultsPerPage = 12;


  const handleViewPayouts = (selectedSeason, username) => {
    const url = `/app/payoutdetails?season=${selectedSeason}&username=${username}`;
    history.push(url);
  };

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
    async function fetchData() {
      try {
        const response = await fetch(`/api/v1/payouts/${selectedSeason}`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setDataTable(data);
        setTotalResults(data.length);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    }

    fetchData();
  }, [selectedSeason]);

  function onPageChangeTable(p) {
    setPageTable(p);
  }

  const totalPages = Math.ceil(totalResults / resultsPerPage);
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
            {sortedData.map((user, i) => (
              <TableRow key={i}>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <Avatar className="hidden mr-3 md:block" src={user.avatar} alt="User avatar" />
                    <div>
                      <p className="font-semibold">{user.username}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="text-sm">{formatAmount(user.amount)}</span>
                </TableCell>
                <TableCell>
                  <Button onClick={() => handleViewPayouts(selectedSeason, user.username)}>View Payouts</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <TableFooter>
          {totalResults > 0 && (
            <Pagination
              totalResults={totalResults}
              resultsPerPage={resultsPerPage}
              onChange={onPageChangeTable}
              label="Table navigation"
            />
          )}
        </TableFooter>
      </TableContainer>
    </>
  );
}

export default Payouts;
