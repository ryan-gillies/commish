import boto3
from decimal import Decimal
import pandas as pd
import sqlalchemy
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from sleeper_wrapper import League
import config.credentials as credentials
from onepassword import OnePassword

class DynamoDBUtils:
    """
    Utility functions for working with DynamoDB.
    """
    op = OnePassword()
    aws_access_key_id = op.get_item(credentials.aws_uuid, 'access_key_id')['access_key_id']
    aws_secret_access_key = op.get_item(credentials.aws_uuid, 'secret_access_key')['secret_access_key']
    region_name = op.get_item(credentials.aws_uuid, 'region')['region']

    def convert_floats_to_decimal(data):
        """
        Recursively convert all float values to Decimal within a nested dictionary or list.

        Args:
            data (dict or list): The data structure to convert.

        Returns:
            dict or list: The converted data structure with float values converted to Decimal.
        """
        if isinstance(data, dict):
            return {
                key: DynamoDBUtils.convert_floats_to_decimal(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [DynamoDBUtils.convert_floats_to_decimal(item) for item in data]
        elif isinstance(data, float):
            return Decimal(str(data))
        else:
            return data
    
    def get_table(table_name):
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=DynamoDBUtils.aws_access_key_id,
            aws_secret_access_key=DynamoDBUtils.aws_secret_access_key,
            region_name=DynamoDBUtils.region_name,
        )
        db_table = dynamodb.Table(table_name)
        return db_table

    def put_item(db_table, partition_key_value, item_data, sort_key_value = None, excluded_keys = None):
        """
        Put an item into DynamoDB table.

        Args:
            db_table (boto3.resources.factory.dynamodb.Table): The DynamoDB table.
            partition_key_value (str): The value of the partition key.
            item_data (dict): The data to be stored as an item in DynamoDB.
            excluded_keys (list): List of keys to exclude from the item_data.

        Returns:
            None
        """
        if excluded_keys is None:
            excluded_keys = []
        
        key_schema = db_table.key_schema
        partition_key_name = key_schema[0]["AttributeName"]
        if len(key_schema) > 1:
            sort_key_name = key_schema[1]["AttributeName"]
        
        key = {partition_key_name: partition_key_value}

        if sort_key_value:
            key[sort_key_name] = sort_key_value

        converted_item_data = DynamoDBUtils.convert_floats_to_decimal(item_data)

        item = {
            **key,
            **{k: v for k, v in converted_item_data.items() if k not in excluded_keys},
        }
        
        try:
            db_table.put_item(Item=item)
            print("Item added successfully")
        except ClientError as e:
            print("Error:", e)

    def store_to_dynamodb(data, table_name, partition_key_value, sort_key_value = None, excluded_keys = None):
        try:
            db_table = DynamoDBUtils.get_table(table_name)
            DynamoDBUtils.put_item(db_table, partition_key_value, data, sort_key_value=sort_key_value, excluded_keys=excluded_keys)
        except ClientError as e:
            print("Error storing data to DynamoDB:", e)

    def load_from_dynamodb(table_name, partition_key_value):
        try:
            db_table = DynamoDBUtils.get_table(table_name)
            key_schema = db_table.key_schema
            partition_key_name = key_schema[0]["AttributeName"]
            response = db_table.query(
                KeyConditionExpression=Key(partition_key_name).eq(partition_key_value)
            ) 
            items = response["Items"]
            if items:
                return items[0]
            else:
                return None
        except ClientError as e:
            print("Error loading league data from DynamoDB:", e)
            return None


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
            "postgresql://retool:pubA9CUnmK5F@ep-icy-salad-54868721.us-west-2.retooldb.com/retool?sslmode=require"
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