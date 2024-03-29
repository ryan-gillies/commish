import unittest
from unittest.mock import patch
from league import League
from backend.models.pools.pool import (
    PropPool,
    HighestScoreOfWeekPool,
    HighestScoringMarginOfWeekPool,
    HighestScoringPlayerOfWeekPool,
    RegularSeasonFirstPlacePool,
    RegularSeasonMostPointsPool,
    RegularSeasonMostPointsAgainstPool,
    RegularSeasonHighestScoringPlayerPool,
    OneWeekHighestScorePool,
    OneWeekHighestScoreAgainstPool,
    OneWeekHighestScoringPlayerPool,
    OneWeekSmallestMarginPool,
    OpeningWeekWinnersPool,
    RivalryWeekWinnersPool,
    LastWeekWinnersPool,
)


class TestPropPool(unittest.TestCase):
    def setUp(self):
        self.mock_league = League()  # Create a mock league object
        self.pool = PropPool("prop_pool_1", self.mock_league, 0.5)

    @patch('builtins.input', return_value="123456")  # Mock the input function to return a roster ID
    def test_set_pool_winner_valid(self, mock_input):
        # Test setting the winner with a valid roster ID
        self.pool.set_pool_winner()
        self.assertEqual(self.pool.winner, [{"roster_id": "123456"}])


class TestHighestScoreOfWeekPool(unittest.TestCase):
    def setUp(self):
        self.mock_league = League()  # Create a mock league object
        self.pool = HighestScoreOfWeekPool(self.mock_league, 0.5, 1)

    def test_set_pool_winner(self):
        # Test setting the winner for the highest score of the week pool
        self.pool.set_pool_winner()
        self.assertIsNotNone(self.pool.winner)


class TestHighestScoringMarginOfWeekPool(unittest.TestCase):
    def setUp(self):
        self.mock_league = League()  # Create a mock league object
        self.pool = HighestScoringMarginOfWeekPool(self.mock_league, 0.5, 1)

    def test_set_pool_winner(self):
        # Test setting the winner for the highest scoring margin of the week pool
        self.pool.set_pool_winner()
        self.assertIsNotNone(self.pool.winner)


class TestHighestScoringPlayerOfWeekPool(unittest.TestCase):
    def setUp(self):
        self.mock_league = League()  # Create a mock league object
        self.pool = HighestScoringPlayerOfWeekPool(self.mock_league, 0.5, 1)

    def test_set_pool_winner(self):
        # Test setting the winner for the highest scoring player of the week pool
        self.pool.set_pool_winner()
        self.assertIsNotNone(self.pool.winner)


# Similar test classes for other pool subclasses...

if __name__ == '__main__':
    unittest.main()
