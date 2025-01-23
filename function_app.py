import azure.functions as func
import logging
import pymssql
import json
import os
import re

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Configuração da conexão com o banco de dados SQL Server
def get_db_connection() -> pymssql.Connection:
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")

    return pymssql.connect(server, username, password, database)

@app.route(route="produtos", methods=['get'])
def getAllProducts(req: func.HttpRequest) -> func.HttpResponse:

    try:
        cursor: pymssql.Cursor = get_db_connection().cursor()

        cursor.execute("SELECT Id, Nome, Descricao, Preco, QuantidadeEstoque, Categoria FROM [dbo].[Produtos]")

        produtos = [ 
            {
                "id":   row[0],
                "nome": row[1],
                "descircao": row[2],
                "preco": float(row[3]),
                "quantidade_estoque": row[4],
                "categoria": row[5],
            } for row in cursor.fetchall() 
        ]

        return func.HttpResponse(json.dumps(produtos), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return func.HttpResponse("Error fetching products data.", status_code=500)

@app.route(route="produtos/{id}", methods=['get'])
def getProductById(req: func.HttpRequest) -> func.HttpResponse:

    product_id = req.route_params["id"]

    if not re.match(r'^\d+$', product_id):
        return func.HttpResponse("Malformed parameter. Expected integer Id.", mimetype="text/plain", status_code=400)

    try:
        cursor: pymssql.Cursor = get_db_connection().cursor()
        
        cursor.execute("""
            SELECT 
                Id,
                Nome,
                Descricao,
                Preco,
                QuantidadeEstoque,
                Categoria
            FROM [dbo].[Produtos]
            WHERE Id = %d
        """, product_id)

        row = cursor.fetchone()

        if row == None:
            return func.HttpResponse("Resource not found in database.", mimetype="text/plain", status_code=404)

        produto = {
            "id":   row[0],
            "nome": row[1],
            "descircao": row[2],
            "preco": float(row[3]),
            "quantidade_estoque": row[4],
            "categoria": row[5],
        }

        return func.HttpResponse(json.dumps(produto), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return func.HttpResponse("Error fetching products data.", status_code=500)