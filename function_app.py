import azure.functions as func
import logging
from pyodbc import Cursor, Row
import pyodbc
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Configuração da conexão com o banco de dados SQL Server
def get_db_connection() -> pyodbc.Connection:
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")

    driver = "{ODBC Driver 18 for SQL Server}"

    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    print(conn_str)

    return pyodbc.connect(conn_str)
 