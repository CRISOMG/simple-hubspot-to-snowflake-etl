import os
from dotenv import load_dotenv
from snowflake.connector import DictCursor
import snowflake.connector

load_dotenv()


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
        return None


def get_snowflake_b2b_vs_b2c_deals():
    connection = get_snowflake_connection()
    if connection is None:
        return {"error": "No se pudo conectar a Snowflake"}

    cursor = connection.cursor(DictCursor)
    try:
        SQL_QUERY = """
            SELECT
                COUNT(CASE WHEN DEALS."associated_company_id" IS NOT NULL THEN 1 END) AS total_deals_b2b,
                COUNT(CASE WHEN DEALS."associated_company_id" IS NULL THEN 1 END)     AS total_deals_b2c,
                COUNT(*) AS total_deals
            FROM
                DEALS;
            """
        cursor.execute(SQL_QUERY.strip())
        result = cursor.fetchone()
    except Exception as e:
        print(f"Error en la consulta: {e}")
        return {"error": str(e)}
    finally:
        cursor.close()
        connection.close()

    return result
