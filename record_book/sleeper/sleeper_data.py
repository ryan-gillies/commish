import pandas as pd
import sqlalchemy
from sleeper_wrapper import League
from record_book.connection import connect_retool

def store_to_postgres(table_name: str, data: pd.DataFrame, con: sqlalchemy.engine.base.Connection, schema: str = "sleeper", dtype: dict = None, if_exists: str = "append"):
    """
    Loads data into the specified database table.

    Args:
        table_name (str): The name of the table in the database.
        data (pd.DataFrame): The data to be loaded into the table.
        con (sqlalchemy.engine.base.Connection): The database connection.
        schema (str): The schema of the table (default: "sleeper").
        dtype (dict): Dictionary specifying the data types for columns (default: None).
        if_exists (str): Action to take if the table already exists (default: "append").
    """
    try:
        data.to_sql(table_name, con=con, schema=schema, dtype=dtype, if_exists=if_exists, index=False)
        print(f"{table_name.capitalize()} added to destination.")
    except sqlalchemy.exc.IntegrityError:
        print(f"Primary Keys already exist...skipping {table_name}.")
    con.close()

def load_matchups(league_id: str, week: int):
    """
    Loads the league's matchups for the given week.

    Args:
        league_id (str): The Sleeper ID for the league.
        week (int): The Sleeper week number.
    """
    con = connect_retool()
    matchups_data = pd.DataFrame(League(league_id).get_matchups(week))
    matchups_data["league_id"] = league_id
    matchups_data["week"] = week
    load_data_to_database("sleeper_matchups", matchups_data, con, dtype={"players_points": sqlalchemy.types.JSON})

def load_playoffs(league_id: str):
    """
    Loads the league's playoff results.

    Args:
        league_id (str): The Sleeper ID for the league.
    """
    con = connect_retool()
    playoffs_data = pd.DataFrame(League(league_id).get_playoff_winners_bracket())
    playoffs_data["league_id"] = league_id
    playoffs_data.rename(columns={"t2": "team2", "t1": "team1", "w": "winner", "l": "loser", "r": "round_id", "m": "matchup_id"}, inplace=True)
    load_data_to_database("sleeper_playoffs", playoffs_data, con, dtype={"t2_from": sqlalchemy.types.JSON, "t1_from": sqlalchemy.types.JSON})
