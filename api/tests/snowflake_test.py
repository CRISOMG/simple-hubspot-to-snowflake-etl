# test_api.services.snowflake.py
import unittest
from unittest.mock import patch, MagicMock, ANY
from snowflake.connector import DictCursor

import api.services.snowflake


class TestSnowflakeUtils(unittest.TestCase):
    MOCK_ENV = {
        "SNOW_USER": "test_user",
        "SNOW_PASSWORD": "test_pass",
        "SNOW_ACCOUNT": "test_account",
        "SNOW_WAREHOUSE": "test_wh",
        "SNOW_DATABASE": "test_db",
        "SNOW_SCHEMA": "test_schema",
        "SNOW_ROLE": "test_role",
    }

    @patch("api.services.snowflake.snowflake.connector.connect")
    @patch.dict("os.environ", MOCK_ENV)
    def test_get_snowflake_connection_success(self, mock_connect):
        """Prueba que la conexión se crea con las credenciales correctas."""

        mock_conn_obj = MagicMock()
        mock_connect.return_value = mock_conn_obj

        conn = api.services.snowflake.get_snowflake_connection()

        self.assertEqual(conn, mock_conn_obj)

        mock_connect.assert_called_once_with(
            user="test_user",
            password="test_pass",
            account="test_account",
            warehouse="test_wh",
            database="test_db",
            schema="test_schema",
            role="test_role",
        )

    @patch("api.services.snowflake.snowflake.connector.connect")
    @patch.dict("os.environ", MOCK_ENV)
    def test_get_snowflake_connection_failure(self, mock_connect):
        """Prueba que la conexión retorna None si snowflake.connector falla."""

        mock_connect.side_effect = Exception("Fallo de conexión")

        conn = api.services.snowflake.get_snowflake_connection()

        self.assertIsNone(conn)

    @patch("api.services.snowflake.get_snowflake_connection")
    def test_get_deals_b2b_vs_b2c_success(self, mock_get_connection):
        """Prueba que la consulta se ejecuta y retorna los datos correctamente."""

        mock_data = {"TOTAL_DEALS_B2B": 10, "TOTAL_DEALS_B2C": 5, "TOTAL_DEALS": 15}

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_data

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        mock_get_connection.return_value = mock_connection

        result = api.services.snowflake.get_snowflake_b2b_vs_b2c_deals()

        self.assertEqual(result, mock_data)

        mock_get_connection.assert_called_once()
        mock_connection.cursor.assert_called_once_with(DictCursor)
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("api.services.snowflake.get_snowflake_connection")
    def test_get_deals_b2b_vs_b2c_query_fails(self, mock_get_connection):
        """Prueba el manejo de error si la consulta (cursor.execute) falla."""

        mock_cursor = MagicMock()
        test_error = Exception("Error de SQL")
        mock_cursor.execute.side_effect = test_error

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        mock_get_connection.return_value = mock_connection

        result = api.services.snowflake.get_snowflake_b2b_vs_b2c_deals()

        self.assertEqual(result, {"error": str(test_error)})

        mock_connection.cursor.assert_called_once_with(DictCursor)
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_not_called()

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("api.services.snowflake.get_snowflake_connection")
    def test_get_deals_b2b_vs_b2c_connection_fails(self, mock_get_connection):
        """Prueba qué pasa si la conexión inicial falla."""
        mock_get_connection.return_value = None

        result = api.services.snowflake.get_snowflake_b2b_vs_b2c_deals()
        self.assertEqual(result, {"error": "No se pudo conectar a Snowflake"})


if __name__ == "__main__":
    unittest.main()
