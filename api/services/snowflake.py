import os
from dotenv import load_dotenv

load_dotenv()

import snowflake.connector


def get_snowflake_connection():
    try:

        conn = snowflake.connector.connect(
            user=os.getenv("SNOW_USER"),
            password=os.getenv("SNOW_PASSWORD"),
            account=os.getenv("SNOW_ACCOUNT"),
            warehouse=os.getenv("SNOW_WAREHOUSE"),
            database=os.getenv("SNOW_DATABASE"),
            schema=os.getenv("SNOW_SCHEMA"),
            role=os.getenv("SNOW_ROLE"),
        )

        return conn
    except Exception as e:
        print(f"Error conectando a Snowflake: {e}")
