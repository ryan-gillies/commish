import boto3
from decimal import Decimal
import pandas as pd
import sqlalchemy
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from sleeper_wrapper import League
from .config.credentials import aws_uuid

class PostgreSQLUtils:
    """
    Utility functions for working with PostgreSQL.
    """
    
    def store_to_postgresql(
        table_name: str,
        data: pd.DataFrame,
        schema: str = "sleeper",
        dtype: dict = None,
        if_exists: str = "append",
    ):
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
        con = sqlalchemy.create_engine(
            "postgresql://retool:ZHVhmOA2Tb4i@ep-icy-salad-54868721.us-west-2.retooldb.com/retool?sslmode=require"
        ).connect()
        try:
            data.to_sql(
                table_name,
                con=con,
                schema=schema,
                dtype=dtype,
                if_exists=if_exists,
                index=False,
                method="multi",
                chunksize=1000,
            )
            print(f"{table_name.capitalize()} added to destination.")
        except sqlalchemy.exc.IntegrityError:
            print(f"Primary Keys already exist...skipping {data}.")
        con.close()


    # @staticmethod
    # def load_playoffs(league_id: str):
    #     """
    #     Loads the league's playoff results.

    #     Args:
    #         league_id (str): The Sleeper ID for the league.
    #     """
    #     con = PostgreSQLUtils.connect_retool()
    #     playoffs_data = pd.DataFrame(League(league_id).get_playoff_winners_bracket())
    #     playoffs_data["league_id"] = league_id
    #     playoffs_data.rename(
    #         columns={
    #             "t2": "team2",
    #             "t1": "team1",
    #             "w": "winner",
    #             "l": "loser",
    #             "r": "round_id",
    #             "m": "matchup_id",
    #         },
    #         inplace=True,
    #     )
    #     PostgreSQLUtils.store_to_postgresql(
    #         "sleeper_playoffs",
    #         playoffs_data,
    #         con,
    #         dtype={"t2_from": sqlalchemy.types.JSON, "t1_from": sqlalchemy.types.JSON},
    #     )