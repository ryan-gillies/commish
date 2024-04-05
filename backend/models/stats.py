"""
Stats Module
============

This module provides classes for retrieving statistics related to league matchups and player performances.

Classes:
- Stats: Abstract base class for retrieving statistics.
- MatchupStats: Subclass of Stats for retrieving matchup statistics.
- PlayerStats: Subclass of Stats for retrieving player statistics.
- LeagueStats: Subclass of Stats for retrieving league-wide statistics.
"""

from abc import ABC


class Stats(ABC):
    """
    Abstract base class for retrieving statistics.
    """

    @staticmethod
    def filter_out_optouts(stats, league):
        """
        Filters out matchups with teams that have opted out.

        Args:
            stats (list of dict): A list of matchups or stats.
            optouts (set): A set of optout roster IDs.

        Returns:
            list of dict: A filtered list of matchups or stats without teams that have opted out.
        """
        return [x for x in stats if x.get("roster_id") not in league.optouts]


class MatchupStats(Stats):
    """
    Subclass of Stats for retrieving matchup statistics.

    Methods:
        get_small_scoring_margin(week=None, top_n=1): Gets the team with the smallest margin of loss for a specific week.
        get_high_scoring_margin(week=None, top_n=1): Finds the team(s) with the highest scoring margin for a specific week.
        get_high_team_score(week=None, top_n=1): Gets the high scoring team(s) for a given week or the entire season.
        get_high_score_against(week=None, top_n=1): Gets the team with the highest score against for a specific week.
        get_head_to_head_winners(week=None): Gets the roster IDs of the matchup winners for the specified week or all weeks if week is None.
    """

    def get_small_scoring_margin(league, week=None, top_n=1):
        """
        Gets the team with the smallest margin of loss for a specific week.

        Args:
            league (League): The League instance.
            week (int): The week number to calculate the small scoring margin. If None, considers the entire season.
            top_n (int): The number of top teams to return. Default is 1.

        Returns:
            list: A list of dictionaries containing week, matchup_id, and matchup_margin.
        """
        if week is not None:
            head_to_head = [
                match for match in league.head_to_head if match.get("week") == week
            ]
        else:
            head_to_head = [
                match for match in league.head_to_head
            ]

        eligible_margins = Stats.filter_out_optouts(head_to_head, league)
        sorted_margins = sorted(
            eligible_margins, key=lambda x: x["matchup_margin"], reverse=False
        )
        return [
            {
                "week": match["week"],
                "matchup_id": match["matchup_id"],
                "roster_id": match["matchup_loser"],
                "matchup_margin": match["matchup_margin"],
                "opponent": match["matchup_winner"],
            }
            for match in sorted_margins[:top_n]
        ]

    def get_high_scoring_margin(league, week=None, top_n=1):
        """
        Finds the team(s) with the highest scoring margin for a specific week.

        Args:
            week (int): The week number to filter matchups. If None, all weeks are considered.
            top_n (int): The number of top teams to return. Default is 1.

        Returns:
            list: A list of dictionaries containing week, matchup_id, and matchup_margin.
        """

        if week is not None:
            head_to_head = [
                match for match in league.head_to_head if match.get("week") == week
            ]
        else:
            head_to_head = [
                match for match in league.head_to_head
            ]

        eligible_margins = Stats.filter_out_optouts(head_to_head, league)
        sorted_margins = sorted(
            eligible_margins, key=lambda x: x["matchup_margin"], reverse=True
        )
        return [
            {
                "week": match["week"],
                "matchup_id": match["matchup_id"],
                "roster_id": match["matchup_winner"],
                "matchup_margin": match["matchup_margin"],
                "opponent": match["matchup_loser"],
            }
            for match in sorted_margins[:top_n]
        ]

    def get_high_team_score(league, week=None, top_n=1):
        """
        Gets the high scoring team(s) for a given week or the entire season.

        Args:
            week (int): The week number to calculate the high score. If None, calculates for the entire season.
            top_n (int): The number of top teams to return. Default is 1.

        Returns:
            List[dict]: A list of dictionaries containing information about the top N teams with the high score.
        """

        all_team_scores = []
        if week is None:
            for week_num, week_matchups in league.matchups.items():
                for matchup in week_matchups:
                    matchup["week"] = week_num
                eligible_matchups = Stats.filter_out_optouts(week_matchups, league)
                all_team_scores.extend(eligible_matchups)
        else:
            week_matchups = league.matchups.get(week, [])
            for matchup in week_matchups:
                matchup["week"] = week  # Ensure "week" key is present
            eligible_matchups = Stats.filter_out_optouts(week_matchups, league)
            all_team_scores.extend(eligible_matchups)

        top_teams = sorted(all_team_scores, key=lambda x: x["points"], reverse=True)[
            :top_n
        ]
        return [
            {
                "week": team["week"],
                "matchup_id": team["matchup_id"],
                "roster_id": team["roster_id"],
                "points": team["points"],
            }
            for team in top_teams
        ]

    def get_high_score_against(league, week=None, top_n=1):
        """
        Gets the team with the highest score against for a specific week.

        Args:
            week (int): The week number to filter matchups. If None, all weeks are considered.
            top_n (int): The number of top teams to return. Default is 1.

        Returns:
            list: A list of dictionaries containing week, matchup_id, and winner_points.
        """

        if week is not None:
            head_to_head = [match for match in league.head_to_head.get(week, [])]
        else:
            head_to_head = [match for match in league.head_to_head]

        eligible_scores_against = Stats.filter_out_optouts(head_to_head, league)
        sorted_scores_against = sorted(
            eligible_scores_against, key=lambda x: x["winner_points"], reverse=True
        )
        top_teams = sorted_scores_against[:top_n]
        return [
            {
                "week": team["week"],
                "matchup_id": team["matchup_id"],
                "roster_id": team["matchup_loser"],
                "winner_points": team["winner_points"],
                "opponent": team["matchup_winner"],
            }
            for team in top_teams
        ]

    def get_head_to_head_winners(league, week=None):
        """
        Gets the roster IDs of the matchup winners for the specified week or all weeks if week is None.

        Args:
            week (int): The week number to filter matchups. If None, all weeks are considered.

        Returns:
            List[dict]: A list of dictionaries containing roster IDs of the matchup winners.
        """

        filtered_head_to_head = Stats.filter_out_optouts(league.head_to_head, league)
        winners = []
        if week is None:
            winners = [
                {
                    "week": match["week"],
                    "matchup_id": match["matchup_id"],
                    "matchup_winner": match["matchup_winner"],
                }
                for match in filtered_head_to_head
            ]
        else:
            winners = [
                {
                    "week": match["week"],
                    "matchup_id": match["matchup_id"],
                    "matchup_winner": match["matchup_winner"],
                }
                for match in filtered_head_to_head
                if match["week"] == week
            ]
        return winners


class PlayerStats(Stats):
    """
    Subclass of Stats for retrieving player statistics.

    This class specializes in retrieving statistics related to player performances
    within league matchups. It provides methods to extract player scores and identify
    high-scoring players for a given week or the entire season.

    Attributes:
        league_id (int): The ID of the league.
        start_week (int): The starting week.
        end_week (int): The ending week.
        player_scores (list of dict): A list of dictionaries containing player scores.

    Methods:
        fetch_player_scores(): Retrieves player scores from matchups for the specified weeks.
        get_high_player_score(week=None, top_n=1): Finds the top N players with the highest score for a given week or the entire season.
        get_regular_season_high_scoring_player(top_n=1): Finds the top N players with the highest cumulative score over all weeks of the regular season.

    Inherits from:
        Stats: Abstract base class for retrieving statistics.
    """

    def get_high_player_score(league, week=None, top_n=1):
        """
        Finds the roster ID of the player with the high score in a given week and returns it.

        Args:
            week (int or None): The week number to filter player scores. If None, all weeks are considered.
            top_n (int): The number of top players to return.

        Returns:
            list: The list of top scoring players.
        """
        if week is None:
            eligible_player_scores = Stats.filter_out_optouts(
                league.player_stats, league
            )
        else:
            eligible_player_scores = Stats.filter_out_optouts(
                [score for score in league.player_stats if score["week"] == week],
                league,
            )
        high_scoring_player = sorted(
            eligible_player_scores, key=lambda x: x["score"], reverse=True
        )[:top_n]
        return high_scoring_player

    def get_regular_season_high_scoring_player(league, top_n=1):
        """
        Finds the top N players with the highest cumulative score over all weeks, excluding players from opted-out rosters.

        Args:
            top_n (int): The number of top players to return.

        Returns:
            list: A list of dictionaries containing information about the highest scoring players, each including player ID, total score, roster ID, player position, and player name.
        """
        player_totals = {}
        player_info = {}
        for player in league.player_stats:
            player_id = player["player_id"]
            score = player["score"]
            roster_id = player["roster_id"]
            position = player["position"]
            player_name = player["player_name"]

            if roster_id in league.optouts:
                continue

            if player_id in player_totals:
                player_totals[player_id] += score
            else:
                player_totals[player_id] = score

            if player_id not in player_info:
                player_info[player_id] = {
                    "roster_id": roster_id,
                    "position": position,
                    "player_name": player_name,
                }

        top_players = []
        sorted_player_ids = sorted(player_totals, key=player_totals.get, reverse=True)
        for player_id in sorted_player_ids[:top_n]:
            top_player_info = {
                "player_id": player_id,
                "total_score": player_totals[player_id],
                "roster_id": player_info[player_id]["roster_id"],
                "position": player_info[player_id]["position"],
                "player_name": player_info[player_id]["player_name"],
            }
            top_players.append(top_player_info)

        return top_players


class LeagueStats(Stats):
    """
    Subclass of Stats for retrieving league-wide statistics.

    Methods:
        get_regular_season_first_place(top_n=1): Retrieves the rosters that finished in the first place during the regular season.
        get_regular_season_most_points(top_n=1): Retrieves the rosters with the most accumulated points during the regular season.
        get_regular_season_most_points_against(top_n=1): Retrieves the rosters with the highest accumulated points against during the regular season.
    """

    def get_regular_season_first_place(league, top_n=1):
        """
        Retrieves the rosters that finished in the first place during the regular season.

        Args:
            top_n (int): The number of top rosters to return. Default is 1.

        Returns:
            list: A list of dictionaries containing information about the top rosters, including roster ID, total wins, and total points for.
        """
        eligible_rosters = [
            team
            for team in league.team_stats
            if team.get("roster_id") not in league.optouts
        ]
        sorted_rosters = sorted(
            eligible_rosters,
            key=lambda x: (x["total_wins"], x["total_points_for"]),
            reverse=True,
        )
        top_teams = sorted_rosters[:top_n]
        return [team for team in top_teams]

    def get_regular_season_most_points(league, top_n=1):
        """
        Retrieves the rosters with the most accumulated points during the regular season.

        Args:
            top_n (int): The number of top rosters to return. Default is 1.

        Returns:
            list: A list of dictionaries containing information about the top rosters, including roster ID and total points for.
        """
        eligible_rosters = [
            team
            for team in league.team_stats
            if team.get("roster_id") not in league.optouts
        ]
        sorted_rosters = sorted(
            eligible_rosters, key=lambda x: x["total_points_for"], reverse=True
        )
        top_teams = sorted_rosters[:top_n]
        return [team for team in top_teams]

    def get_regular_season_most_points_against(league, top_n=1):
        """
        Retrieves the rosters with the highest accumulated points against during the regular season.

        Args:
            top_n (int): The number of top rosters to return. Default is 1.

        Returns:
            list: A list of dictionaries containing information about the top rosters, including roster ID and total points against.
        """
        eligible_rosters = [
            team
            for team in league.team_stats
            if team.get("roster_id") not in league.optouts
        ]
        sorted_rosters = sorted(
            eligible_rosters, key=lambda x: x["total_points_against"], reverse=True
        )
        top_teams = sorted_rosters[:top_n]
        return [team for team in top_teams]
