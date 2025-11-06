import os
from dotenv import load_dotenv

load_dotenv()

from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector


def load_data(df_deals, df_leads):
    print("Iniciando carga a Snowflake...")

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

        print("Conexión a Snowflake exitosa.")

        # Cargar Deals
        # 'if_exists='replace'' borra la tabla y la crea de nuevo.
        write_pandas(
            conn,
            df_deals,
            "DEALS",  # Nombre de la tabla en Snowflake
            auto_create_table=True,  # Crea la tabla si no existe
            overwrite=True,
            use_logical_type=True,
        )

        # Cargar Leads
        write_pandas(
            conn,
            df_leads,
            "LEADS",  # Nombre de la tabla en Snowflake
            auto_create_table=True,
            overwrite=True,
            use_logical_type=True,
        )

        print("Carga a Snowflake completada.")

    except Exception as e:
        print(f"Error cargando a Snowflake: {e}")
    finally:
        if "conn" in locals():
            conn.close()
