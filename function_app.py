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
                "descricao": row[2],
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
            "descricao": row[2],
            "preco": float(row[3]),
            "quantidade_estoque": row[4],
            "categoria": row[5],
        }

        return func.HttpResponse(json.dumps(produto), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return func.HttpResponse("Error fetching products data.", status_code=500)

@app.route(route="produtos", methods=['post'])
def createProduct(req: func.HttpRequest) -> func.HttpResponse:
    try:
        product_data = req.get_json()

        # Validação básica dos campos obrigatórios
        required_fields = ["nome", "descricao", "preco", "quantidade_estoque", "categoria"]
        if not all(field in product_data for field in required_fields):
            return func.HttpResponse("Missing required fields.", mimetype="text/plain", status_code=400)

        conn = get_db_connection()
        cursor: pymssql.Cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO [dbo].[Produtos] (Nome, Descricao, Preco, QuantidadeEstoque, Categoria)
            VALUES (%s, %s, %s, %s, %s)
        """, (product_data["nome"], product_data["descricao"], product_data["preco"], 
              product_data["quantidade_estoque"], product_data["categoria"]))

        conn.commit()

        return func.HttpResponse("Product created successfully.", status_code=201)

    except Exception as e:
        logging.error(f"Database operation failed: {e}")
        return func.HttpResponse("Error creating product.", status_code=500)

@app.route(route="produtos/{id}", methods=['put'])
def updateProductById(req: func.HttpRequest) -> func.HttpResponse:
    product_id = req.route_params["id"]

    if not re.match(r'^\d+$', product_id):
        return func.HttpResponse("Malformed parameter. Expected integer Id.", mimetype="text/plain", status_code=400)

    try:
        product_data = req.get_json()

        # Validação básica dos campos obrigatórios
        required_fields = ["nome", "descricao", "preco", "quantidade_estoque", "categoria"]
        
        if not all(field in product_data for field in required_fields):
            return func.HttpResponse("Missing required fields.", mimetype="text/plain", status_code=400)

        conn = get_db_connection()
        cursor: pymssql.Cursor = conn.cursor()

        cursor.execute("""
            UPDATE [dbo].[Produtos]
            SET Nome = %s, Descricao = %s, Preco = %s, QuantidadeEstoque = %s, Categoria = %s
            WHERE Id = %s
        """, (product_data["nome"], product_data["descricao"], product_data["preco"], 
              product_data["quantidade_estoque"], product_data["categoria"], product_id))

        if cursor.rowcount == 0:
            return func.HttpResponse("Resource not found in database.", mimetype="text/plain", status_code=404)

        conn.commit()

        return func.HttpResponse("Product updated successfully.", status_code=200)

    except Exception as e:
        logging.error(f"Database operation failed: {e}")
        return func.HttpResponse("Error updating product.", status_code=500)

@app.route(route="produtos/{id}", methods=['delete'])
def deleteProductById(req: func.HttpRequest) -> func.HttpResponse:

    product_id = req.route_params["id"]

    if not re.match(r'^\d+$', product_id):
        return func.HttpResponse("Malformed parameter. Expected integer Id.", mimetype="text/plain", status_code=400)

    try:
        conn = get_db_connection()
        cursor: pymssql.Cursor = conn.cursor()
        
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
            "descricao": row[2],
            "preco": float(row[3]),
            "quantidade_estoque": row[4],
            "categoria": row[5],
        }

        cursor.execute("""
            DELETE FROM [dbo].[Produtos] WHERE Id = %d
        """, product_id)

        conn.commit()

        return func.HttpResponse(json.dumps(produto), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return func.HttpResponse("Error fetching products data.", status_code=500)

# Rota para servir o arquivo openapi.yaml
@app.route(route="openapi.yaml", methods=['get'])
def openapi_yaml(req: func.HttpRequest) -> func.HttpResponse:
    with open('docs/openapi.yaml', 'r') as file:
        openapi_yaml_content = file.read()
    return func.HttpResponse(openapi_yaml_content, mimetype="application/yaml")

# Rota para servir o Swagger UI
@app.route(route="swagger-ui.html", methods=['get'])
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    with open('swagger-ui.html', 'r') as file:
        swagger_ui_content = file.read()
    return func.HttpResponse(swagger_ui_content, mimetype="text/html")
