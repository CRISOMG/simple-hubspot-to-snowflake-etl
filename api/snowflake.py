import os
import snowflake.connector
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configuración de la conexión (leída desde .env)
SNOW_USER = os.getenv("SNOW_USER")
SNOW_PASSWORD = os.getenv("SNOW_PASSWORD")
SNOW_ACCOUNT = os.getenv("SNOW_ACCOUNT")
SNOW_DATABASE = os.getenv("SNOW_DATABASE")
SNOW_SCHEMA = os.getenv("SNOW_SCHEMA")
SNOW_WAREHOUSE = os.getenv("SNOW_WAREHOUSE")


def get_db_connection():
    """Crea y retorna una nueva conexión a Snowflake."""
    return snowflake.connector.connect(
        user=SNOW_USER,
        password=SNOW_PASSWORD,
        account=SNOW_ACCOUNT,
        database=SNOW_DATABASE,
        schema=SNOW_SCHEMA,
        warehouse=SNOW_WAREHOUSE,
    )


def log_data_to_snowflake(event_name: str, payload: dict):
    """
    Se conecta a Snowflake e inserta un registro en la tabla API_LOGS.
    """
    conn = None
    try:
        conn = get_db_connection()
        print("Conexión a Snowflake exitosa.")

        # Usamos 'to_json_string' si 'payload' es un dict,
        # para insertarlo correctamente en el tipo VARIANT
        import json

        payload_str = json.dumps(payload)

        sql = """
        INSERT INTO API_LOGS (EVENT_NAME, PAYLOAD)
        VALUES (%s, PARSE_JSON(%s))
        """

        # Ejecutar el INSERT
        conn.cursor().execute(sql, (event_name, payload_str))
        print(f"Datos insertados: {event_name}")

    except Exception as e:
        print(f"Error al escribir en Snowflake: {e}")
        # En una app real, aquí manejarías el error de forma más robusta
        raise e
    finally:
        if conn:
            conn.close()
            print("Conexión a Snowflake cerrada.")
