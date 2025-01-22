import azure.functions as func
import logging
from pyodbc import Cursor, Row
import pyodbc
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
